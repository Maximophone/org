import os
import json
from _settings import _SETTINGS

class Container(object):
	def _key_in(self,key):
		for k in self.__dict__:
			if key == k.split('_')[0]: return True
		return False

	def _add(self,key,value):
		if self._key_in(key):
			if key in self.__dict__:
				prev_value = getattr(self,key)
				new_key = key + '_' + prev_value._path[-2]
				self._add(new_key,prev_value)
				delattr(self,key)
			new_key = key + '_' + value._path[-2]
			self._add(new_key,value)
		else:
			setattr(self,key,value)

def _grow(node,d):
	if d.get('content'): node._content = d.get('content')
	if d.get('elements'):
		for element in d.get('elements'):
			new_node = node._add(element.get('content'))
			_grow(new_node,element)
	if d.get('subs'):
		for sub,subd in d.get('subs').iteritems():
			new_node = node.meta._add(sub)
			_grow(new_node,subd)

def _create():
	result = {}
	with open(_SETTINGS['save_file'],'r') as savefile:
		result = json.loads(savefile.read())
	origin = RootNode()
	_grow(origin,result)
	return origin

def _save():
	with open(_SETTINGS['save_file'],'w') as savefile:
		savefile.write(json.dumps(_ORIGIN._dict))

def _reset():
	with open(_SETTINGS['save_file'],'w') as savefile:
		savefile.write(json.dumps({}))

def saver(function):
	def inner(*args,**kwargs):
		result = function(*args,**kwargs)
		_save()
		return result
	return inner

class Meta(object):
	def __init__(self,node):
		self._node = node

	def _process_string(self,s):
		return s.replace(' ','').replace('_','').lower()

	def _add(self,sub,params={},node=None,**kwargs):
		if node is None: node = OrgNode(params,parent=self._node,path=self._node._path+[sub],**kwargs)
		setattr(self._node,sub,node)
		self._node._subs[sub] = node
		_GOTO._add(sub,node)
		return node

	@saver
	def add(self,sub,params={},**kwargs):
		return self._add(sub,params,**kwargs)

class OrgNode(object):
	def __init__(self,content=None,params={},parent=None,path=[],**kwargs):
		self.meta = Meta(self)
		self._params = params.copy()
		self._params.update(kwargs)
		self._elements = []
		self._subs = {}
		self._content = content
		self._parent = parent
		self._path = path

	@property
	def content(self):
		return self._content

	@content.setter
	@saver
	def content(self,value):
		self._content = value


	@property
	def _dict(self):
		d = {}
		if self._content: d['content'] = self._content
		if self._subs: d['subs'] = {k:v._dict for k,v in self._subs.iteritems()}
		if self._elements: d['elements'] = [e._dict for e in self._elements]
		return d

	def _add(self,text):
		node = OrgNode(text,parent=self)
		self._elements.append(node)
		return node

	@saver
	def add(self,text):
		self._add(text)

	def _search_content(self,text):
		if not self._content: return False
		content = self._content.lower()
		return content.find(text)>=0

	def _self_search(self,text):
		results = []
		if self._search_content(text):
			results.append(self)
		for element in self._elements:
			results += element._self_search(text)
		return results

	def _search(self,text):
		results = []
		results += self._self_search(text)
		for sub in self._subs.values():
			results += sub._search(text)
		return results

	def __str__(self):
		return str(self._dict)

	def __repr__(self):
		return str(self)

class RootNode(OrgNode):
	def __init__(self):
		self.goto = _GOTO
		super(RootNode,self).__init__()

	def search(self,text):
		return self._search(text)

	def _reset(self):
		_reset()

_GOTO = Container()
_ORIGIN = _create()

if __name__ == '__main__':
	o = _ORIGIN

	
	


