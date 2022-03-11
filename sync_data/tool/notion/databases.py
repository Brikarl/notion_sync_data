# -*- coding: utf-8 -*-
# @Author  : Qliangw
# @Time    : 2022/2/27 21:29
# @Function: notion 数据库处理

import json
import re

import requests

from sync_data.tool.douban.data.enum_data import MediaInfo, MediaStatus, MediaType
from sync_data.utils import log_detail
from sync_data.tool.notion import base
from sync_data.utils.http_utils import RequestUtils


def get_body(data_dict, database_id, media_status, media_type):
    """
    获取json数据

    :param media_type:
    :param media_status:
    :param data_dict:
    :param database_id:
    :return:
    """
    status = ""
    music_status = ""
    if media_status == MediaStatus.WISH.value:
        status = "想看"
        music_status = "想听"
    elif media_status == MediaStatus.DO.value:
        status = "在看"
        music_status = "在听"
    elif media_status == MediaStatus.COLLECT.value:
        status = "看过"
        music_status = "听过"
    else:
        status = ""
        music_status = ""

    log_detail.info(f"【RUN】{media_type}数据信息整理为json格式")
    rat = data_dict[MediaInfo.RATING_F.value]
    rating = float(rat) if rat == "" else 0
    if media_type == MediaType.MUSIC.value:
        body = {
            "parent": {
                "type": "database_id",
                "database_id": f"{database_id}"
            },
            "properties": {
                "音乐": {
                    "title": [{
                        "type": "text",
                        "text": {
                            "content": data_dict[MediaInfo.TITLE.value]
                        }
                    }]
                },
                "封面": {
                    "files": [{
                        "type": "external",
                        "name": data_dict[MediaInfo.IMG.value][-13:],
                        "external": {
                            "url": data_dict[MediaInfo.IMG.value]
                        }
                    }]
                },
                "评分": {
                    "number": rating
                },
                "表演者": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": data_dict[MediaInfo.PERFORMER.value]
                        }
                    }]
                },
                "发行时间": {
                    "select": {
                        "name": data_dict[MediaInfo.RELEASE_DATE.value][0:4]
                    }
                },
                "标记状态": {
                    "select": {
                        "name": f"{music_status}"
                    }
                },
                "豆瓣链接": {
                    "url": f"{data_dict[MediaInfo.URL.value]}"
                }
            }
        }
        return body
    elif media_type == MediaType.MOVIE.value:
        pass
    elif media_type == MediaType.BOOK.value:
        body = {
            "parent": {
                "type": "database_id",
                "database_id": f"{database_id}"
            },
            "properties": {
                "书名": {
                    "title": [{
                        "type": "text",
                        "text": {
                            "content": data_dict[MediaInfo.TITLE.value]
                        }
                    }]
                },
                "ISBN": {
                    "url": f"https://isbnsearch.org/isbn/{data_dict[MediaInfo.ISBN.value]}"
                },
                "封面": {
                    "files": [{
                        "type": "external",
                        "name": data_dict[MediaInfo.IMG.value][-13:],
                        "external": {
                            "url": data_dict[MediaInfo.IMG.value]
                        }
                    }]
                },
                "评分": {
                    "number": rating
                },
                "作者": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": data_dict[MediaInfo.AUTHOR.value]
                        }
                    }]
                },
                "出版年份": {
                    "select": {
                        "name": data_dict[MediaInfo.PUB_DATE.value][0:4]
                    }
                },
                "出版社": {
                    "select": {
                        "name": data_dict[MediaInfo.PUBLISHER.value]
                    }
                },
                "价格": {
                    "number": float(data_dict[MediaInfo.PRICE.value])
                },
                "评分人数": {
                    "number": int(data_dict[MediaInfo.ASSESS.value])
                },
                "页数": {
                    "number": int(data_dict[MediaInfo.PAGES.value])
                },
                "标记状态": {
                    "select": {
                        "name": f"{status}"
                    }
                },
                "豆瓣链接": {
                    "url": f"{data_dict[MediaInfo.URL.value]}"
                }
            }
        }
        return body


def create_database(token, page_id, media_type):
    """
    创建新的数据库
    :param media_type: 媒体类型 book music tv movie
    :param token: notion->setting->integrations->develop your own integrations
    :param page_id: 浏览器打开notion，链接的尾部获取
    :return: databases_id，可以通过该id定位到数据库
    """
    # TODO 添加书 影 音 数据库
    create_db_data = {}
    if media_type == MediaType.BOOK.value:
        create_db_data = {
            "parent": {"type": "page_id", "page_id": f"{page_id}"},
            "title": [{"type": "text", "text": {"content": "豆瓣书单库"}}],
            "icon": {"type": "emoji", "emoji": "📚"},
            "properties": {
                "书名": {"title": {}},
                "评分": {"number": {}},
                "豆瓣链接": {"url": {}},
                "作者": {"rich_text": {}},
                "出版社": {"select": {}},
                "ISBN": {"url": {}},
                "封面": {"files": []},
                "出版年份": {"select": {}},
                "价格": {"number": {}},
                "评分人数": {"number": {}},
                "页数": {"number": {}},
                "短评": {"rich_text": {}},
                "类型": {"multi_select": {}},
                "标记状态": {"select": {}},
                "标记时间": {"date": {}},
                "个人评分": {"select": {"options": [
                    {"name": "⭐", "color": "yellow"},
                    {"name": "⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐⭐⭐", "color": "yellow"}]}},
            }}
    elif media_type == MediaType.MUSIC.value:
        create_db_data = {
            "parent": {"type": "page_id", "page_id": f"{page_id}"},
            "title": [{"type": "text", "text": {"content": "豆瓣音乐库"}}],
            "icon": {"type": "emoji", "emoji": "🎵"},
            "properties": {
                "音乐": {"title": {}},
                "表演者": {"rich_text": {}},
                "封面": {"files": []},
                "评分": {"number": {}},
                "出版者": {"select": {}},
                "发行时间": {"select": {}},
                "ISRC": {"url": {}},
                "豆瓣链接": {"url": {}},
                "评分人数": {"number": {}},
                "短评": {"rich_text": {}},
                "类型": {"multi_select": {}},
                "标记状态": {"select": {}},
                "标记时间": {"date": {}},
                "个人评分": {"select": {"options": [
                    {"name": "⭐", "color": "yellow"},
                    {"name": "⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐⭐⭐", "color": "yellow"}]}},
            }}
    elif media_type == MediaType.MOVIE.value:
        """
        类型是获取豆瓣中的信息
            剧情 / 动作 / 科幻/ 犯罪
        分类是个人主观分的
            电视剧、电影、动画片（指的是电影）、动漫（剧集）、纪录片（电影和电视剧）
        """
        create_db_data = {
            "parent": {"type": "page_id", "page_id": f"{page_id}"},
            "title": [{"type": "text", "text": {"content": "豆瓣影视库"}}],
            "icon": {"type": "emoji", "emoji": "🎬"},
            "properties": {
                "名字": {"title": {}},
                "评分": {"number": {}},
                "豆瓣链接": {"url": {}},
                "导演": {"rich_text": {}},
                "编剧": {"rich_text": {}},
                "主演": {"multi_select": {}},
                "类型": {"multi_select": {}},
                "分类": {"select": {}},
                "国家地区": {"multi_select": {}},
                "IMDb": {"url": {}},
                "封面": {"files": []},
                "时间": {"select": {}},
                "片长": {"number": {}},
                "评分人数": {"number": {}},
                "简介": {"rich_text": {}},
                "标记状态": {"select": {}},
                "标记时间": {"date": {}},
                "个人评分": {"select": {"options": [
                    {"name": "⭐", "color": "yellow"},
                    {"name": "⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐⭐", "color": "yellow"},
                    {"name": "⭐⭐⭐⭐⭐", "color": "yellow"}]}},
            }}
    else:
        exit("暂不支持其他数据库的创建")

    try:
        if create_db_data:
            log_detail.info(f"【RNU】创建{media_type}数据库--初始化参数")
            db_data = base.NotionBaseInfo(token=token)
            params = json.dumps(create_db_data)
            # print(params)
            log_detail.debug(f"【RNU】创建{media_type}数据库--post请求")
            # res = RequestUtils.post(url=db_data.get_db_url(), params=params, headers=db_data.get_headers())
            db_res = RequestUtils()
            res = db_res.post(url=db_data.get_db_url(), params=params, headers=db_data.get_headers())
            if res.status_code == 200:
                log_detail.debug(res.text)
                database_id = eval(res.text.replace(":null", ":'null'").replace(":false", ":'false'"))["id"]
                return database_id
            else:
                exit("创建数据库失败，请检查是否页面有授权给【集权】，再重新使用本程序")
        else:
            log_detail.warn(f"【RUN】跳过创建{media_type}数据库")
    except Exception as err:
        exit(f"网络请求错误:{err}")


def update_database(data_dict, database_id, token, media_status, media_type):
    """
    写入数据库

    :param media_type: 媒体类型
    :param data_dict: 待写入数据字典
    :param database_id: 数据库id
    :param token:【必须】
    :param media_status: 标记状态
    :return: TODO 返回一个成功后的页面ID
    """
    try:
        body = get_body(data_dict=data_dict,
                        database_id=database_id,
                        media_status=media_status,
                        media_type=media_type)
        body = json.dumps(body)
        page_data = base.NotionBaseInfo(token)
        req = RequestUtils()
        res = req.post(url=page_data.get_page_url(),
                       headers=page_data.get_headers(),
                       params=body)
        if res.status_code == 200:
            log_detail.info(f'【RUN】导入《{data_dict[MediaInfo.TITLE.value]}》成功。媒体链接：{data_dict["url"]}')
            return None
        else:
            log_detail.error(f'【RUN】导入《{data_dict[MediaInfo.TITLE.value]}》失败：{res.content}！媒体链接：{data_dict["url"]}')
    except Exception as err:
        log_detail.error(f'【RUN】导入数据库错误：{err}！媒体链接：{data_dict["url"]}')
    finally:
        log_detail.error(f'【RUN】data_dict 参数有误!')


