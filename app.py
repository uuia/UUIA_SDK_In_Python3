from controler.uuia_controller import app
from util.uuid_logger import Uuia_logger

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)