#include <windows.h>
#include "http/restclient.hpp"
#include "json.hpp"
#include <iostream>
#include <string>
#include <fstream>
#include <unordered_map>

namespace fs = std::filesystem;
using json = nlohmann::json;

static std::unordered_map<int, std::string> ItemIDData;

int main() {
	std::setlocale(LC_ALL, ".utf8");

	std::string url = "https://api-takumi.mihoyo.com/event/e20200928calculate/v1/avatar/list";

	RestClient::Request request;

	request.headers["Origin"] = "https://act.mihoyo.com";
	request.headers["Referer"] = "https://act.mihoyo.com/";
	request.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0";
	request.headers["x-rpc-device_id"] = "7d6e5d90-d0e3-4594-938f-34b3d77aecf8";
	request.headers["Accept"] = "application/json, text/plain, */*";

	json postData = {
		{"element_attr_ids", json::array()},
		{"weapon_cat_ids", json::array()},
		{"page", 1},
		{"size", 200},
		{"is_all", true},
		{"lang", "zh-cn"}
	};
	std::string data = postData.dump();

	RestClient::Response response = RestClient::post(url, "application/json;charset=UTF-8", data, &request);

	std::cout << "HTTP Status Code: " << response.code << std::endl;

	try {
		json jsonData = json::parse(response.body);
		
		if (jsonData.contains("data") && jsonData["data"].contains("list")) {
			json list = jsonData["data"]["list"];
			for (const auto& item : list) {
				if (item.contains("id") && item.contains("name")) {
					int id = item["id"].get<int>();
					std::string name = item["name"].get<std::string>();
					ItemIDData[id] = name;
					//std::cout << "id: " << id << ", name: " << name << std::endl;
				}
			}
		}

		std::cout << "Total unique items in ItemIDData: " << ItemIDData.size() << std::endl;
		for (auto Item: ItemIDData)
		{
			std::cout << "id: " << Item.first << ", name: " << Item.second << std::endl;

		}
	} catch (const json::parse_error& e) {
		std::cerr << "JSON parse error: " << e.what() << std::endl;
	}

	return 0;
}