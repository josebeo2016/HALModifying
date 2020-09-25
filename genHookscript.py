template = """
try{
	hookall("[class]","[method]","a");
}catch(err){
	send("[-]Error in: [class].[method]");
}
"""
old = []
for x in open("Sensitive_APIs.csv","r").readlines():
	if(x not in old):
		old.append(x)
		classname = x.split(',')[0].strip()
		metname = x.split(',')[1].strip()
		if metname.lower() == "constructor":
			metname = "$init"
		content = template.replace("[class]",classname)
		content = content.replace("[method]",metname)
		f=open("hook.txt","a+").write(content)


