import asyncio
import tornado
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Sarah has successfully gotten this to run. B\"H")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

async def main():
    app = make_app()
    app.listen(3000)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
