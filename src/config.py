class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'diego'
    MYSQL_PASSWORD = '1234'
    MYSQL_DB = 'api_utl'

config={
    'development':DevelopmentConfig
}