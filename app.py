from controler.uuia_controller import app
from util.uuid_logger import Uuia_logger

if __name__ == '__main__':
    Uuia_logger().i("we湖工大","启动！")
    app.run()