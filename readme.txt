如何使用：
在拉下image之后运行：
	docker run -d --name "随便" -p "any_free_port":8000 \
	-e another_key="your_own_api" -e openai_key="your_openai_api" -e web_key="your_web_api" \
	-e DISASTER_LLM_MODEL="your_model_name" -e DISASTER_LLM_BASE_URL="model_url"
	"image_name"

#这里的“随便”是你给容器的名字，"any_free_port"在上下文是服务器中同一个可用的空端口
#上述三个api第一个是你任意一个兼容openai的sdk的模型的api，第二个是openai模型api，第三个是高德web服务api。
#"image_name"就是拉下来的image的名字。
#如果调用openai模型，加上-e DISASTER_LLM_PROVIDER="openai"，不然的话可以不加，默认会使用另一个。
#上面的disaster_llm_model就写使用的模型，disaster_llm_base_url就写模型使用的url。


然后即可运行，有两种模式，1为运行单条，2为运行多条。

如下是检测单条：
	curl -s -X POST http://"服务器ip":"any_free_port"/verify \
  	-H "Content-Type: application/json" \
  	-d '{"text":"any_text"}'

#上文中的"any_text"就是待检测文本，"服务器ip"就是部署该容器的服务器的ip

如下是检测多条：
	curl -N -s -X POST http://"服务器ip":"any_free_port"/verify_batch \
        -H "Content-Type: application/json" \
        -d '{"texts":["text1", "text2", "text3"]}'


#基本同上，["text1", "text2", "text3"]list可延长，而且-d后也可跟一个json文件，内容和这个同样格式。
#如果想输出格式好一点，则在最后加上|jq .来自动缩进，对于检测单条同理。
