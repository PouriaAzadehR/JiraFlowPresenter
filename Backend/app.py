from factory.create_app import create_app
from config import settings

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=settings.APP_PORT)
