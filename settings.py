# coding=utf-8
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'djaildhjsdfhjs'
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USER', 'it@onmath.cn')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWD', 'e*lDEp8g2TKXe3aJ')
    MAIL_SUBJECT_PREFIX = '[WheatDB]'
    MAIL_SENDER = 'WheatDB <{0}>'.format(MAIL_USERNAME)
    # Celery
    CELERY_RESULT_BACKEND = 'redis://:wheatdb@localhost:6379/0'
    CELERY_BROKER_URL = 'redis://:wheatdb@localhost:6379/0'
    CELERY_POOL_RESTARTS = True
    # VCF file
    VCF_FILE_PATH = '/data/wheatdb/data/vcf_private'
    VCF_TABLE_PATH = '/data/wheatdb/data/vcf_private_table'
    VCF_SAMPLE_PATH = '/data/wheatdb/data/vcf_private_sample'
    VCF_TABLE_BYCHR_PATH = '/data/wheatdb/data/vcfTablePkl/'
    VCF_ANN_BYCHR_PATH = '/data/wheatdb/data/vcfannDB/'
    COMPLETE_CHROM_SIZE = '/data/wheatdb/data/ref/full.chr.size'
    CHROM_SIZE = '/data/wheatdb/data/ref/clean.chr.size'
    GENE_POS = '/data/wheatdb/data/ref/gene.5kbupdown.window.bed'
    IMG_PATH = '/static/download/imgs'
    UPLOADED_PHOTOS_DEST = '/static/download/photos'
    DEFAULT_USER_PHOTO = '/static/images/user.svg'
    SCRIPT_PATH = '/data/scripts'
    EXTRACT_VCF_SAMPLE = 'extract_vcf_sample_name.sh'
    SPLIT_VCF_SAMPLE = 'splitt_vcf_to_each_sample.sh'
    VCF_SEQ = 'vcf2seq.py'
    VCF_ANN = 'vcf_ann.sh'
    VCF_PCA = 'plink2pca.sh'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_MAP = {
        'qq.com': 'https://mail.qq.com',
        '163.com': 'https://mail.163.com'
    }
    CACHE = {
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_HOST': '127.0.0.1',
        'CACHE_REDIS_PORT': 6379,
        'CACHE_REDIS_PASSWORD': 'wheatdb',
        'CACHE_REDIS_DB': 0
    }
    CACHE_PREFIX = 'wheatgmap'

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    ENV = 'dev'
    DB_NAME = 'dev.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, DB_NAME)
    Debug = True


class TestConfig(Config):
    ENV = 'test'
    DB_NAME = 'test.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, DB_NAME)
    Debug = True


class ProdConfig(Config):
    ENV = 'prod'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{passwd}@{host}/{db}'.format(
        user=os.environ.get('DB_USER', 'wheatdb'),
        passwd=os.environ.get('DB_PASSWD', 'wheatdb'),
        host='localhost',
        db='wheatDB')
    Debug = False


config = {
    'default': DevConfig,
    'test': TestConfig,
    'prod': ProdConfig,
    'dev': DevConfig
}
