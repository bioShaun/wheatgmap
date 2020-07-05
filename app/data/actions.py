from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import String, Column, Integer, Text, DateTime, Boolean
from flask import abort
from math import ceil
from app.auth.models import Data


filter_null = lambda x: x if x else '-'


class DT(Data):
    def __init__(self, **kwargs):
        self.draw = kwargs['draw']
        self.page = kwargs['length']
        self.length = kwargs['length']
        self.search_str = kwargs['search']
        self.order_str = kwargs['order']
        self.columns = self.to_list()
        self._query = None

    def result(self, **kwargs):
        if kwargs:
            self._query = Data.query.filter_by(**kwargs)
        else:
            self._query = Data.query
        self.search()
        self.order()
        return self.pager()

    def to_list(self):
         return [c.name for c in self.__table__.columns][1:-3]

    def search(self):
        if self.search_str:
            try:
                col, pattern = self.search_str.split(':')
                self.like(col, pattern)
            except:
                pass

    def order(self):
        if self.order_str:
            order_type, index = self.order_str.split()
            col = self.columns[int(index)]
            if order_type == 'desc':
                self._query = self._query.order_by((getattr(Data, col).desc()))
            else:
                self._query = self._query.order_by(getattr(Data, col))

    def like(self, col, keyword):
        self._query = self._query.filter(getattr(Data, col).like('%{}%'.format(keyword)))

    def pager(self):
        pagination = self._query.paginate(page=self.page, per_page=self.length, error_out=True)
        recordsTotal = self._query.count()
        objs = pagination.items
        rs = []
        for obj in objs:
            rs.append({attr: filter_null(getattr(obj, attr)) for attr in self.columns})
        res = {
            'draw': self.draw,
            'recordsTotal': recordsTotal,
            'recordsFiltered': recordsTotal,
            'data': rs
        }
        return res
