import json
from py2neo import *
from django.shortcuts import render

# 连接数据库
graph = Graph('http://localhost:7474/', auth=('neo4j', 'root'))


def search_all():
    # 定义data数组，存放节点信息
    data = []
    # 定义关系数组，存放节点间的关系
    links = []
    # 查询所有节点，并将节点信息取出存放在data数组中
    for n in graph.nodes:
        # 将节点信息转化为json格式，否则中文会不显示
        nodesStr = json.dumps(graph.nodes[n], ensure_ascii=False)
        # 取出节点的name
        node_name = json.loads(nodesStr)['name']
        # 构造字典，存储单个节点信息
        dict = {
            'name': node_name,
            'symbolSize': 50,
            'category': '对象'
        }
        # 将单个节点信息存放在data数组中
        data.append(dict)
    # 查询所有关系，并将所有的关系信息存放在links数组中
    rps = graph.relationships
    for r in rps:
        # 取出开始节点的name
        source = str(rps[r].start_node['name'])
        # 取出结束节点的name
        target = str(rps[r].end_node['name'])
        # 取出开始节点的结束节点之间的关系
        name = str(type(rps[r]).__name__)
        # 构造字典存储单个关系信息
        dict = {
            'source': source,
            'target': target,
            'name': name
        }
        # 将单个关系信息存放进links数组中
        links.append(dict)
    # 输出所有节点信息
    # for item in data:
    #     print(item)
    # 输出所有关系信息
    # for item in links:
    #     print(item)
    # 将所有的节点信息和关系信息存放在一个字典中
    neo4j_data = {
        'data': data,
        'links': links
    }
    neo4j_data = json.dumps(neo4j_data)
    return neo4j_data


def search_one(value):
    # 定义data数组存储节点信息
    data = []
    # 定义links数组存储关系信息
    links = []
    # 查询节点是否存在
    node = graph.run('MATCH(n:person{name:"' + value + '"}) return n').data()
    # 如果节点存在len(node)的值为1不存在的话len(node)的值为0
    if len(node):
        # 如果该节点存在将该节点存入data数组中
        # 构造字典存放节点信息
        dict = {
            'name': value,
            'symbolSize': 50,
            'category': '对象'
        }
        data.append(dict)
        # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
        nodes = graph.run('MATCH(n:person{name:"' + value + '"})<-->(m:person) return m').data()
        # 查询该节点所涉及的所有relationship，无向，步长为1，并返回这些relationship
        reps = graph.run('MATCH(n:person{name:"' + value + '"})<-[rel]->(m:person) return rel').data()
        # 处理节点信息
        for n in nodes:
            # 将节点信息的格式转化为json
            node = json.dumps(n, ensure_ascii=False)
            node = json.loads(node)
            # 取出节点信息中person的name
            name = str(node['m']['name'])
            # 构造字典存放单个节点信息
            dict = {
                'name': name,
                'symbolSize': 50,
                'category': '对象'
            }
            # 将单个节点信息存储进data数组中
            data.append(dict)
        # 处理relationship
        for r in reps:
            source = str(r['rel'].start_node['name'])
            target = str(r['rel'].end_node['name'])
            name = str(type(r['rel']).__name__)
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            links.append(dict)
        # 构造字典存储data和links
        search_neo4j_data = {
            'data': data,
            'links': links
        }
        # 将dict转化为json格式
        search_neo4j_data = json.dumps(search_neo4j_data)
        return search_neo4j_data
    else:
        # print("查无此节点")
        return 0


def index(request):
    ctx = {}
    if request.method == 'POST':
        # 接收前端传过来的查询值
        node_name = request.POST.get('node')
        # 查询结果
        search_neo4j_data = search_one(node_name)
        # 未查询到该节点
        if search_neo4j_data == 0:
            ctx = {'title': '数据库中暂未添加该实体'}
            neo4j_data = search_all()
            return render(request, 'index.html', {'neo4j_data': neo4j_data, 'ctx': ctx})
        # 查询到了该节点
        else:
            neo4j_data = search_all()
            return render(request, 'index.html',
                          {'neo4j_data': neo4j_data, 'search_neo4j_data': search_neo4j_data, 'ctx': ctx})

    neo4j_data = search_all()
    return render(request, 'index.html', {'neo4j_data': neo4j_data, 'ctx': ctx})
