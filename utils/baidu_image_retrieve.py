from aip import AipImageSearch
import json


class BaiduImageSearch(object):
    # 获得连接对象
    APP_ID = '16842923'
    API_KEY = 'BXngiNhk6QxRR2kEhbcbrCAI'
    SECRET_KEY = 'A7NeGhtiNw2WUzbSNfGkRQVzQv3Z57yg'
    client = None

    def __init__(self):
        self.client = AipImageSearch(self.APP_ID, self.API_KEY, self.SECRET_KEY)


    # 获取图片
    def get_file_content(self,file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()


    def upload(self,path,good_id,sku_id):
        """ 调用相似图检索—入库, 图片参数为本地图片 """
        image = self.get_file_content(path)
        """ 如果有可选参数 """
        options = {}
        params = {}
        params['key'] = path
        params['good_id'] = good_id
        params['sku_id'] = sku_id
        options["brief"] =  json.dumps(params)
        # print(options)

        """ 带参数调用相似图检索—入库, 图片参数为本地图片 """
        res = self.client.similarAdd(image, options)
        # client.similarAddUrl(url, options) # 远程图片
        return res

    def upload_remote_url(self,url,good_id,sku_id):
        
        """ 如果有可选参数 """
        pass
        # options = {}
        # params = {}
        # params['key'] = url
        # params['good_id'] = good_id
        # params['sku_id'] = sku_id
        # options["brief"] =  json.dumps(params)
        # print(options)

        # # """ 带参数调用相似图片搜索—入库, 图片参数为远程url图片 """
        # res = self.client.similarAddUrl(url, options)
        # return res





    def delete(self,key):
        """ 调用删除相似图，图片参数为远程url图片 """
        url = 'http://tbcdn.tajansoft.com/'+key
        self.client.similarDeleteByUrl(url)

    def search(self,path):
        image = self.get_file_content(path)
        res = self.client.similarSearch(image)
        return res
    # """ 如果有可选参数 """
    # options = {}
    # options["tags"] = "100,11"
    # options["tag_logic"] = "0"
    # options["pn"] = "100"
    # options["rn"] = "250"

    # """ 带参数调用相似图检索—检索, 图片参数为本地图片 """
    # client.similarSearch(image, options)




