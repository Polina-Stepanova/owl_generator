# -*- coding: utf-8 -*-
"""OntologyFromCSVgen.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fEiqWJ7W1W76KsHVuzlDOPGZWpjd9k_P
"""

import xml.etree.ElementTree as ET
import sys
import pandas as pd

if(len(sys.argv)) < 3:
  print("Укажите входной .csv и выходной .owl файлы (опционально - выходной .txt файл для списка всех уникальных терминов).\n")
  sys.exit()
#(первый аргумент - имя самой программы) второй - имя csv, третий-owl, четвертый если надо - имя файла куда сбросить списком-множество терминов (ну уж множество отношений алфавитной сортировкой собственной таблицы можно выяснить да???)

name_csv=sys.argv[1]
name_owl=sys.argv[2]
name_termlist=""
if(len(sys.argv)>3):
  name_termlist=sys.argv[3]


csv_table=pd.read_csv(name_csv)

#ET.register_namespace("owl","http://www.w3.org/2002/07/owl#")
#ET.register_namespace("rdf","http://www.w3.org/1999/02/22-rdf-syntax-ns#")
#ET.register_namespace("rdfs","http://www.w3.org/2000/01/rdf-schema#")
#ET.register_namespace("xsd","http://www.w3.org/2001/XMLSchema#")
#почему-то не добавляются в получаемый файл, хотя rdf точно присутствует в тегах, поэтому вставляем напрямую
root = ET.Element("rdf:RDF",{"xmlns:owl":"http://www.w3.org/2002/07/owl#",
                             "xmlns:rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                             "xmlns:rdfs":"http://www.w3.org/2000/01/rdf-schema#",
                             "xmlns:xsd":"http://www.w3.org/2001/XMLSchema#"})


reltypes=set(list(csv_table['SubRole']))#собирается множество всех различных вносимых отношений
reltypes.discard('вид')#для род-вид - особый порядок генерации
for rt in list(reltypes):
   ET.SubElement(root, "owl:ObjectProperty", {"rdf:ID":'имеет_'+rt.replace(' ','_')} )#в любых словосочетаниях пробелы заменяются на нижние подчеркивания (для корректной работы средств визуализации и т.п.)

tclasses=set(list(csv_table['MainTerm']))#множество всех терминов(=классов)
tclasses.update(list(csv_table['SubTerm']))
for cl in tclasses:
  #для каждого термина создается класс
  currclass=ET.SubElement(root, "owl:Class", {"rdf:ID":cl.replace(' ','_')} )

  #все пары род-вид где этот термин - подкласс (вид):
  s1_subclass=csv_table[(csv_table['SubTerm']==cl)&(csv_table['SubRole']=="вид")]
  for supercl in s1_subclass['MainTerm']:
     ET.SubElement(currclass,"rdfs:subClassOf" , {"rdf:resource":'#'+supercl.replace(' ','_')})
  s1_rel=csv_table[(csv_table['MainTerm']==cl)&(csv_table['SubRole']!="вид")] #выбираем из оставшихся только пары, где этот класс-термин в каком-то отношении в _главной_ роли (для род-вид роль была _подчиненная_ - спец. случай)

  #по парам отношений НЕ род-вид, где данный термин выступает в главной роли (целое для части-целого и т.п.):
  #в описание класса добавляются все отношения как свойства класса
  for supercl_rel in zip(s1_rel['SubTerm'],s1_rel['SubRole']):
     ET.SubElement(currclass,"имеет_"+supercl_rel[1].replace(' ','_') , {"rdf:resource":'#'+supercl_rel[0].replace(' ','_')})

#библиотечная генерация xml не предусматривает переносы для читабельности (переносы и сдвиги добавляются в качестве текста (внутреннего или стоящего после них) элементов xml-дерева)
def pretty_print_ET(tree, parent=None, index=-1, depth=0):
    for i, node in enumerate(tree):
        pretty_print_ET(node, tree, i, depth + 1)#для сдвига строки нужно добавить перевод строки и сдвиг(табуляции) в качестве "текста" в предыдущей строке
        #смотрим в каждое поддерево
        #накапливая сдвиг
        #у внутренних нужно объемлющим дописать перевод и сдвиг+1, в конце внутренней если она последняя нужно дописать перевод и сдвиг (для закрывающего тега, без +1)
    if parent is not None:#для самой первой (корня) ничего не надо
        if index == 0:
            parent.text = '\n' + ('\t' * depth)
        else:
            parent[index - 1].tail = '\n' + ('\t' * depth)
        if index == len(parent) - 1:
            tree.tail = '\n' + ('\t' * (depth - 1))#после последней поддерева для открывающего тега следующего поддерева = на том же сдвиге, что поддерево = без +1


pretty_print_ET(root)
tree = ET.ElementTree(root)
tree.write(name_owl,encoding='utf-8')

#если требуется дополнительно отдельный список всех терминов в отношениях:
if(len(sys.argv)>3):
  with open(name_termlist,'w') as outterm:
    for t in tclasses:
      outterm.write(t)
      outterm.write("\n")

