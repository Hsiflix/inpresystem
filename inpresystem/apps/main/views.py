from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from bs4 import BeautifulSoup as Soup
import xml.etree.ElementTree as xml

url = 'http://127.0.0.1:8000/'
object = None
sortState = 0

#visible, hidden, inherit

class my_object:
    id = ""
    source = ""
    category = ""
    published = ""
    title = ""
    text = ""
    def __init__(self, id, source, category, published, title, text):
        self.id = id
        self.source = source
        self.category = category
        self.published = published
        self.title = title
        self.text = text

class my_objects:
    list_of_objects = []
    find_list_of_objects = []
    actual_list_of_objects = []
    objects = {}
    count = 0
    xml_name = ''
    find_mode = 0
    find_string = ''
    id = 1
    def __init__(self, xml_name):
        self.xml_name = xml_name
        self.list_of_objects = []
        self.objects = {}
        self.count = 0
        with open(xml_name, 'r', encoding='utf-8') as xml:
            soup = Soup(xml.read(), 'lxml')
            for doc in soup.find_all('doc'):
                self.list_of_objects.append(my_object(doc.find('id').text, 
                                                 doc.find('source').text,
                                                 doc.find('category').text,
                                                 doc.find('published').text,
                                                 doc.find('title').text,
                                                 doc.find('text').text))
                self.objects[doc.find('id').text] = self.count
                self.id = int(doc.find('id').text)
                self.count+=1
        self.updateActualList()

    def updateActualList(self):
        global sortState
        sortState = 0
        if self.find_mode == 0:
            self.actual_list_of_objects = self.list_of_objects
        else:
            self.actual_list_of_objects = self.find_list_of_objects

    def create(self, source, category, published, title, text):
        self.list_of_objects.append(my_object(self.id+1, 
                                              source,
                                              category,
                                              published,
                                              title,
                                              text))
        self.save_xml()
    
    def update(self, id, source, category, published, title, text):
        project = self.list_of_objects[int(self.objects.get(f'{int(id)}'))]
        #project.id = id
        project.source = source
        project.category = category
        project.published = published
        project.title = title
        project.text = text
        self.save_xml()

    def delete(self, text_id):
        tmp = self.list_of_objects.pop(int(self.objects.get(f'{int(text_id)}')))
        print(f'UDALYAEM {tmp.id}')
        self.find_string = ''
        self.find_mode = 0
        self.save_xml()

    def find(self, find_str):
        if find_str=='':
            self.find_mode = 0
            self.find_string = find_str
        else:
            self.find_mode = 1
            self.find_string = find_str
        self.find_list_of_objects = []
        find_str = self.find_string.lower()
        for i in self.list_of_objects:
            if i.title.lower().find(find_str) != -1:
                self.find_list_of_objects.append(i)
        self.updateActualList()

    def sort(self, sortState):
        if sortState == 1: #По возрастания
            self.actual_list_of_objects = sorted(self.actual_list_of_objects, key=lambda x: x.title)
        elif sortState == 2: #По убыванию
            self.actual_list_of_objects = sorted(self.actual_list_of_objects, key=lambda x: x.title, reverse=True)
        else: #По умолчанию
            self.updateActualList()

    #Создать корень xml-файла
    def createRootXML(self):
        return xml.Element("docs")

    #Создать итоговый xml-файл
    def createXML(self, root, filename):
        tree = xml.ElementTree(root)
        tree.write(filename, encoding='utf8')

    #Добавить элемент в xml-файл
    def appendRootXML(self, root, element):
        global lock
        root.append(element)

    #Создать XML-элемент
    def createElement(self, **args)->xml.Element:
        xml_root = xml.Element("doc")
        xml_contents = []
        xml_count = 0
        for j, i in args.items():
            xml_contents.append(xml.SubElement(xml_root, j))
            xml_contents[xml_count].set('auto','false')
            xml_contents[xml_count].set('type','str')
            xml_contents[xml_count].set('verify','true')
            xml_contents[xml_count].text = str(i)
            xml_count+=1
        return xml_root

    def save_xml(self):
        xml_root = self.createRootXML()

        for i in self.list_of_objects:
            root = self.createElement(id=i.id, 
                                      source=i.source, 
                                      category=i.category, 
                                      published=i.published, 
                                      title=i.title, 
                                      text=i.text)
            self.appendRootXML(xml_root, root)

        self.createXML(xml_root, self.xml_name)
        self.__init__(self.xml_name)

def index(request):
    global object
    print('INDEX')
    object = my_objects('result.xml')
    return render(request, 'main/index.html', {'url':url, 'xml_file':object, 'CPVisibility':'hidden', 'RPVisibility':'hidden'})

def create_text_button(request):
    global object
    print('CREATEOBJECTBUTTON')
    return render(request, 'main/index.html', {'url':url, 'xml_file':object, 'CPVisibility':'visible', 'RPVisibility':'hidden'})

def find_button(request):
    global object
    find_str = request.POST.get('find', 'N/D')
    print(f'FINDBUTTON: {find_str}')
    object.find(find_str)
    return render(request, 'main/index.html', {'url':url, 'xml_file':object, 'CPVisibility':'hidden', 'RPVisibility':'hidden'})

def sort_button(request):
    global object
    global sortState
    if sortState>=2:
        sortState=0
    else:
        sortState+=1
    print(f'SORTBUTTON: {sortState}')
    object.sort(sortState)
    return render(request, 'main/index.html', {'url':url, 'xml_file':object, 'CPVisibility':'hidden', 'RPVisibility':'hidden'})

def create_text(request):
    global object
    print('CREATEOBJECT')
    object.create(request.POST.get('source', 'N/D'),
                  request.POST.get('category', 'N/D'),
                  request.POST.get('published', 'N/D'),
                  request.POST.get('title', 'N/D'),
                  request.POST.get('text', 'N/D'))
    text = object.list_of_objects[int(object.objects.get(f'{object.id}'))]
    return render(request, 'main/index.html', {'url':url, 'text':text, 'xml_file':object, 'CPVisibility':'hidden', 'RPVisibility':'visible'})

def save_text(request, text_id):
    global object
    print('SAVEOBJECT: '+str(text_id))
    object.update(text_id,
                request.POST.get('source', 'N/D'),
                request.POST.get('category', 'N/D'),
                request.POST.get('published', 'N/D'),
                request.POST.get('title', 'N/D'),
                request.POST.get('text', 'N/D'))
    text = object.list_of_objects[int(object.objects.get(f'{int(text_id)}'))]
    return render(request, 'main/index.html', {'url':url, 'text':text, 'xml_file':object, 'CPVisibility':'hidden', 'RPVisibility':'visible'})

def delete_text(request, text_id):
    global object
    print('DELETEOBJECT: '+str(text_id))
    object.delete(text_id)
    return render(request, 'main/index.html', {'url':url, 'xml_file':object, 'CPVisibility':'hidden', 'RPVisibility':'hidden'})

def review_text(request, text_id):
    global object
    print('REVIEWOBJECT: '+str(text_id))
    text = object.list_of_objects[int(object.objects.get(f'{int(text_id)}'))]
    print(object.list_of_objects[int(object.objects.get(f'{int(text_id)}'))].id)
    return render(request, 'main/index.html', {'url':url, 'text':text, 'xml_file':object, 'CPVisibility':'hidden', 'RPVisibility':'visible'})