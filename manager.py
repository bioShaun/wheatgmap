# coding=utf-8

from flask_script import Manager, Server
from flask_migrate import MigrateCommand
from app.auth.models import User
from app.exetensions import db
from app.app import create_app

app = create_app('prod')
manager = Manager(app)
manager.add_command('runserver',
                    Server(host='0.0.0.0',
                           port=8080))

manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def init_db():
    db.create_all()
    users = [User(username='dongchunhao',
                  email='dongchunhao1222@163.com',
                  password='dong63235455',
                  active=True),
             User(username='chencheng',
                  email='291552579@qq.com',
                  password='050400',
                  active=True,
                  is_admin=True),
             User(username='wheatcaas212',
                  email='zuffer@126.com',
                  password='kong-212',
                  active=True)]
    db.session.add_all(users)
    db.session.commit()
    '''
    tables = [Snptable(tablename='snp_mRNA_snp_ann_table',
                       tabletype='snp',
                       owner='chencheng'),
              Snptable(tablename='expr_gene_tmp_pos',
                       tabletype='expr',
                       owner='chencheng'),
              Snptable(tablename='snp_mRNA_snp_ann_table',
                       tabletype='snp',
                       owner='dongchunhao'),
              Snptable(tablename='snp_mRNA_snp_ann_table',
                       tabletype='snp',
                       owner='wheatcaas212')]
    db.session.add_all(tables)
    db.session.commit()
    '''


if __name__ == '__main__':
    manager.run()
