import asyncio
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, Application
from tornado.escape import json_decode
import json
import datetime
from time import perf_counter
import psycopg2
import os

class MainHandler(RequestHandler):
    def initialize(self):
        self.db = psycopg2.connect("dbname=api_data user=postgres password=postgres")

    async def fetch_api_data(self, url, headers={}):
        start = perf_counter()
        response = await self.http.fetch(url, headers)
        end = perf_counter()
        response_time = int(1000 * (end - start)) # response time in milliseconds
        response_json = json_decode(response.body)

        return response_json, response_time

    async def get(self):
        self.http = AsyncHTTPClient()
        time = datetime.datetime.now()

        # fetch current TLV weather data from VisualCrossing API
        weather_json, weather_response_time = await self.fetch_api_data("https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/tel%20aviv/today?unitGroup=us&elements=temp%2Chumidity%2Cwindspeedmean%2Cvisibility&include=current&key=8JGLTFXE5KMTAPEGXU5TU5V6P&contentType=json")

        # fetch fun fact about today in history from Wikimedia API
        history_json, history_response_time = await self.fetch_api_data("https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/" + time.strftime('%m/%d'), 
                                                                        headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0YjI2ZjUzNjViMTc5OWQ3YTdhNjkxZGUxZWQ1Zjc4ZCIsImp0aSI6IjI1MzQ5NmQwMTQwYTBlNGVmZDI0Y2RjODk3ZDZhYmNlODljODhlY2M4ZDM5ZWNjNDA3ODNiMzhlYWMyMWY1NDE4MzhmNzIwNDc0MGZiZDcwIiwiaWF0IjoxNjg0Mzg3MTU3LjEwOTc2OCwibmJmIjoxNjg0Mzg3MTU3LjEwOTc3MSwiZXhwIjozMzI0MTI5NTk1Ny4xMDc3OCwic3ViIjoiNzI4NDQ2NjAiLCJpc3MiOiJodHRwczovL21ldGEud2lraW1lZGlhLm9yZyIsInJhdGVsaW1pdCI6eyJyZXF1ZXN0c19wZXJfdW5pdCI6NTAwMCwidW5pdCI6IkhPVVIifSwic2NvcGVzIjpbImJhc2ljIl19.YxjPiTevJS6JSITFF2dHAjfNaEQfP6EqcC3gu__1lzrChBOrFIkCHw8wNWUw1S-UbA0xdzvbn2acoJyZ9X3NCMjaLUu6_ZaQ8LZ0jAsGAn16cZG-Ecphd0a0BPl-fUVHGDqIoivD3YWXsx5Aqig1eXXNHURfq3Pzu5aOloZDPnEyhqks1Z4jP3wJ7zMGRFKIh3dTDMx-1mFBgTHYWNNNqJaPQA7cGYiCScoFogjomZIPc0u4Qz8jtwkGic4LLFrAhagIQ4T5TwuRiR48apcdmlbSabgh9RGkDK-JSv9iAAyZwh33aJLRvh7h5Knq8w_D_DO0mUJkZwJMYIh0hhOjO9E-_47z-3ArQLt6bHZe2Y0vMD-hjJyUniP2gjgykb5Aq7ngXgCWfPd1SI2FigsnBcrKXkvcFCsPQcj8bDYwoNZfr4hsrH0RlWLYbC1F6YUWEiq_h-hOE5qyiMGNbQA2ys3T0EZCLZAKpEjns46m3q3NnjYplMSTumyfwbhj5qgV4zc6NomGmUSzurrvYz1_-u_KKh2UVozc7luY1YgFZm0cXZKmreDuptFa3nMWZqC8m3Gja_HsUZjpm0OOmU9d9l2oJC0J6zf_StnIgj7mlvSqYENCLLF6dlB01OhupPKjBlKiE91HIZqLa1sZGFtHxgR2etkK--hJTRFa8AIWhDs', 'User-Agent': 'SarahWebApp'})

        # fetch astronomy image of the day and image info from NASA API
        space_json, space_response_time = await self.fetch_api_data("https://api.nasa.gov/planetary/apod?api_key=rib1eMvde90H5lSNiaQQdPdRChyVUinpT8ZDjRm2")

        # format datetime for SQL format and replace ' with '' for SQL text insertions
        datetime_str = time.strftime('%Y%m%d %I:%M:%S %p')
        img_title = space_json["title"].replace('\'', '\'\'')
        history_fact_text = history_json["events"][-1]["text"].replace('\'', '\'\'')

        # record API data in the api_data database in tables corresponding to each API
        cursor = self.db.cursor()
        cursor.execute(f'INSERT INTO tlv_weather VALUES (\'{datetime_str}\', '
                       f'{weather_response_time}, {weather_json["currentConditions"]["temp"]}, '
                       f'{weather_json["currentConditions"]["humidity"]}, {weather_json["days"][0]["windspeedmean"]}, '
                       f'{weather_json["currentConditions"]["visibility"]});')
        cursor.execute(f'INSERT INTO history_facts VALUES (\'{datetime_str}\', '
                       f'{history_response_time}, \'{history_fact_text}\', '
                       f'{history_json["events"][-1]["year"]});')
        cursor.execute(f'INSERT INTO space_imgs VALUES (\'{datetime_str}\', '
                       f'{space_response_time}, \'{img_title}\', \'{space_json["url"]}\');')
        self.db.commit()

        # store fetched API data in JSON format that can be parsed by JS files
        results_json = json.dumps({
            "time": time.strftime('%m/%d/%Y %I:%M:%S %p'),
            "tlv_weather": {
                "response_time": weather_response_time,
                "temp": weather_json["currentConditions"]["temp"],
                "humidity": weather_json["currentConditions"]["humidity"],
                "windspeed": weather_json["days"][0]["windspeedmean"],
                "visibility": weather_json["currentConditions"]["visibility"],
            },
            "history_facts": {
                "response_time": history_response_time,
                "fact": history_json["events"][-1]["text"],
                "year": history_json["events"][-1]["year"]
            },
            "space_imgs": {
                "response_time": space_response_time,
                "img_title": space_json["title"],
                "img_url": space_json["url"]
            }
        })
        self.write(results_json)
        
    def on_finish(self):
        self.db.close()

    def set_default_headers(self):
        # allows backend to be queried by frontend
        self.set_header("Access-Control-Allow-Origin", "*")

def make_app():
    return Application(
        [(r"/", MainHandler)],
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )

async def main():
    app = make_app()
    app.listen(8888)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
