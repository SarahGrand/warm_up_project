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

    async def get(self):
        http = AsyncHTTPClient()
        time = datetime.datetime.now()

        # fetch current TLV weather data from VisualCrossing API
        start = perf_counter()
        weather_response = await http.fetch("https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/tel%20aviv/today?unitGroup=us&elements=temp&include=current&key=8JGLTFXE5KMTAPEGXU5TU5V6P&contentType=json")
        end = perf_counter()
        weather_response_time = int(1000 * (end - start))
        weather_json = json_decode(weather_response.body)

        # fetch fun fact about today in history from Wikimedia API
        start = perf_counter()
        history_response = await http.fetch("https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/events/" + time.strftime('%m/%d'), headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI0YjI2ZjUzNjViMTc5OWQ3YTdhNjkxZGUxZWQ1Zjc4ZCIsImp0aSI6IjI1MzQ5NmQwMTQwYTBlNGVmZDI0Y2RjODk3ZDZhYmNlODljODhlY2M4ZDM5ZWNjNDA3ODNiMzhlYWMyMWY1NDE4MzhmNzIwNDc0MGZiZDcwIiwiaWF0IjoxNjg0Mzg3MTU3LjEwOTc2OCwibmJmIjoxNjg0Mzg3MTU3LjEwOTc3MSwiZXhwIjozMzI0MTI5NTk1Ny4xMDc3OCwic3ViIjoiNzI4NDQ2NjAiLCJpc3MiOiJodHRwczovL21ldGEud2lraW1lZGlhLm9yZyIsInJhdGVsaW1pdCI6eyJyZXF1ZXN0c19wZXJfdW5pdCI6NTAwMCwidW5pdCI6IkhPVVIifSwic2NvcGVzIjpbImJhc2ljIl19.YxjPiTevJS6JSITFF2dHAjfNaEQfP6EqcC3gu__1lzrChBOrFIkCHw8wNWUw1S-UbA0xdzvbn2acoJyZ9X3NCMjaLUu6_ZaQ8LZ0jAsGAn16cZG-Ecphd0a0BPl-fUVHGDqIoivD3YWXsx5Aqig1eXXNHURfq3Pzu5aOloZDPnEyhqks1Z4jP3wJ7zMGRFKIh3dTDMx-1mFBgTHYWNNNqJaPQA7cGYiCScoFogjomZIPc0u4Qz8jtwkGic4LLFrAhagIQ4T5TwuRiR48apcdmlbSabgh9RGkDK-JSv9iAAyZwh33aJLRvh7h5Knq8w_D_DO0mUJkZwJMYIh0hhOjO9E-_47z-3ArQLt6bHZe2Y0vMD-hjJyUniP2gjgykb5Aq7ngXgCWfPd1SI2FigsnBcrKXkvcFCsPQcj8bDYwoNZfr4hsrH0RlWLYbC1F6YUWEiq_h-hOE5qyiMGNbQA2ys3T0EZCLZAKpEjns46m3q3NnjYplMSTumyfwbhj5qgV4zc6NomGmUSzurrvYz1_-u_KKh2UVozc7luY1YgFZm0cXZKmreDuptFa3nMWZqC8m3Gja_HsUZjpm0OOmU9d9l2oJC0J6zf_StnIgj7mlvSqYENCLLF6dlB01OhupPKjBlKiE91HIZqLa1sZGFtHxgR2etkK--hJTRFa8AIWhDs', 'User-Agent': 'SarahWebApp'})
        end = perf_counter()
        history_response_time = int(1000 * (end - start))
        history_json = json_decode(history_response.body)

        # fetch astronomy image of the day and image info from NASA API
        start = perf_counter()
        space_response = await http.fetch("https://api.nasa.gov/planetary/apod?api_key=rib1eMvde90H5lSNiaQQdPdRChyVUinpT8ZDjRm2")
        end = perf_counter()
        space_response_time = int(1000 * (end - start))
        space_json = json_decode(space_response.body)

        # record API data in the api_data database in tables corresponding to each API
        datetime_str = time.strftime('%Y%m%d %I:%M:%S %p')
        cursor = self.db.cursor()
        cursor.execute(f'INSERT INTO tlv_weather VALUES (\'{datetime_str}\', {weather_response_time}, {weather_json["currentConditions"]["temp"]});')
        cursor.execute(f'INSERT INTO history_facts VALUES (\'{datetime_str}\', {history_response_time}, \'{history_json["events"][-1]["text"]}\', {history_json["events"][-1]["year"]});')
        cursor.execute(f'INSERT INTO space_imgs VALUES (\'{datetime_str}\', {space_response_time}, \'{space_json["title"]}\', \'{space_json["url"]}\');')
        self.db.commit()

        # render html template with info fetched from APIs
        # self.render("template.html", title="Sarah's Web App", temp=weather_json["currentConditions"]["temp"],
        #             year=history_json["events"][-1]["year"], fun_fact=history_json["events"][-1]["text"],
        #             space_img_title=space_json["title"], space_img_url=space_json["url"])

        # store fetched API data in JSON format that can be parsed by JS files
        results_json = json.dumps({
            "time": datetime_str,
            "tlv_weather": {
                "response_time": weather_response_time,
                "temp": weather_json["currentConditions"]["temp"]
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
        # self.render("template_with_react.html", results=results_json)
        self.write(results_json)
        
    def on_finish(self):
        self.db.close()

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def options(self):
        self.set_status(204)
        self.finish()

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
