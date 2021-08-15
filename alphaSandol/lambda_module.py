from bs4 import BeautifulSoup
import requests
import datetime
import json
import boto3
# boto3는 AWS 버킷에 접근하기 위해  import한 모듈로서, 로컬에서 테스트하기에는 어려움이 있음.
# 따라서 버킷에 접근하는 코드의 경우, 메인에 올려서 직접 실행해봐야함.
# 로컬에서 다른 코드 테스트시 오류 방지 하기 위함.
#
# from resource import Constant
from return_type_generator import return_type
from return_type_generator import common_params
import sandol_constant as Constant

GEN = return_type()  # kakao-i type json generator
GEN_OPTION = common_params()  # generator optional param


class AboutMeal:  # 학식 관련 클래스
    def __init__(self):
        self.DATE = 0
        self.LUNCH = 1
        self.DINNER = 2

        self.S3 = boto3.resource('s3')
        self.S3_client = boto3.client('s3')
        self.bucket = self.S3.Bucket(Constant.BUCKET_NAME)
        self.data = ""
        self.URL_MENU = "https://ibook.kpu.ac.kr/Viewer/menu01"

    def read_meal(self) -> dict:  # 학식 불러오기
        MEAL_GEN = return_type()
        try:
            self.bucket.download_file(Constant.RESTAURANT_MENU, Constant.LOCAL_RESTAURANT_MENU)

        except Exception as e:
            return GEN.set_text(
                f"[File-Open-Error #131] 저장소에서 파일을 가져오는데 실패했습니다.{Constant.IMOGE['emotion']['sad']}\n{e}")
        # 버킷을 로컬 임시 폴더에 다운로드

        try:
            weekday = ['월', '화', '수', '목', '금', '토', '일']
            with open(Constant.LOCAL_RESTAURANT_MENU, "r", encoding='UTF-8') as f:
                data = f.readlines()
                for restaurant in range(0, len(data), 2):  # 파일에서 식당 구분이 2칸 간격으로 되어있음
                    menu_list = data[restaurant + 1].replace("\'", '').split(", ")
                    last_update_date = datetime.date.fromisoformat(menu_list[0])
                    if restaurant == 2:  # 웰스프레쉬의 경우 건너뛴다 (링크로 대체)
                        continue

                    form = data[restaurant].replace("\n", '').replace("🐾", Constant.IMOGE['emotion']['walk'])
                    ret = f"{form}[{str(last_update_date)} {weekday[last_update_date.weekday()]}요일]\n" \
                          f"{Constant.IMOGE['emotion']['paw']} 중식 : {menu_list[self.LUNCH]}\n" \
                          f"{Constant.IMOGE['emotion']['paw']} 석식 : {menu_list[self.DINNER]}"
                    MEAL_GEN.set_text(ret, is_init=False)

            return_string = MEAL_GEN.set_text(f"{Constant.IMOGE['emotion']['paw']}웰스프레쉬 [URL 참조]\n{self.URL_MENU}",
                                              is_init=False)
            return return_string

        except Exception as e:
            return GEN.set_text(
                "[File-Open-Error #132] 파일을 여는 중 오류가 발생했어요.." + Constant.IMOGE['emotion']['sad'] + str(e))

    def upload_meal(self, store_name, lunch_list: list, dinner_list: list, input_date, owner_id) -> dict:  # 학식 업로드
        if (owner_id != Constant.RESTAURANT_ACCESS_ID[store_name]) and owner_id not in list(Constant.SANDOL_ACCESS_ID.values()):
            return GEN.set_text(f"[Permission-Error #121-1] 권한이 없습니다{owner_id}{Constant.IMOGE['emotion']['angry']}")
        # 권한 확인

        if store_name not in Constant.RESTAURANT_ACCESS_ID.keys():
            return GEN.set_text(f"[Not-Found-Error #121-2] 해당하는 식당이 없습니다.{Constant.IMOGE['emotion']['sad']}")
        # 식당 존재 여부 확인

        try:
            self.S3.meta.client.download_file(Constant.BUCKET_NAME, Constant.RESTAURANT_MENU,
                                              Constant.LOCAL_RESTAURANT_MENU)

        except Exception as e:
            return GEN.set_text(f"[File-Open-Error #122] 저장소에서 파일을 찾을 수 없습니다.{Constant.IMOGE['emotion']['sad']}\n{e}")

        with open(Constant.LOCAL_RESTAURANT_MENU, "r", encoding="UTF-8") as f:
            try:
                data = f.readlines()
                menu_info = data[data.index("🐾" + store_name + "\n") + 1].replace('\'', '').replace("\n", "").split(
                    ", ")
                menu_info[self.DATE] = input_date

                menu_info[self.LUNCH] = lunch_list.replace(", ", ",").replace(" ", ",")
                menu_info[self.DINNER] = dinner_list.replace(",", "").replace(" ", ",")

                menu_info[self.LUNCH] = lunch_list.replace(" ", ",")
                menu_info[self.DINNER] = dinner_list.replace(" ", ",")

                menu_info[self.LUNCH] = lunch_list.replace(" ", ",")
                menu_info[self.DINNER] = dinner_list.replace(" ", ",")

                data[data.index("🐾" + store_name + "\n") + 1] = str(menu_info)[1:-1] + "\n"  # 최종 문자열
                with open(Constant.LOCAL_RESTAURANT_MENU, "w", encoding='UTF-8') as rf:
                    rf.writelines(data)

            except Exception as e:
                return GEN.set_text(
                    f"[File-Open-Error #123]파일을 수정하는 중 오류가 발생했습니다.{Constant.IMOGE['emotion']['sad']}\n{e}")

            try:
                s3 = boto3.client('s3')  # 이 부분 해당 버킷 생성 후 적절히 수정 예정
                s3.upload_file(Constant.LOCAL_RESTAURANT_MENU, 'sandol', Constant.RESTAURANT_MENU)

            except Exception as e:
                return GEN.set_text(
                    f"[File-Open-Error #124]파일을 저장소에 업로드하는 중 오류가 발생했습니다.{Constant.IMOGE['emotion']['sad']}\n{e}")

        return GEN.set_text(f"네! 학생들에게 잘 전달할게요! 감사합니다!{Constant.IMOGE['emotion']['walk']}")

    def reset_meal(self, bot_id, date) -> dict:  # 학식 초기화
        if bot_id not in list(Constant.SANDOL_ACCESS_ID.values()):
            return GEN.set_text(f"[Permission-Error #141] 권한이 없습니다{Constant.IMOGE['emotion']['angry']}")

        try:
            self.S3.meta.client.download_file(Constant.BUCKET_NAME, Constant.RESTAURANT_MENU,
                                              Constant.LOCAL_RESTAURANT_MENU)

        except Exception as e:
            return GEN.set_text(f"[File-Open-Error #122] 저장소에서 파일을 찾을 수 없습니다.{Constant.IMOGE['emotion']['sad']}\n{e}")

        try:
            with open(Constant.LOCAL_RESTAURANT_MENU, "w", encoding="UTF-8") as f:
                rest_name = [f"{Constant.IMOGE['emotion']['paw']}미가식당\n",
                             f"{Constant.IMOGE['emotion']['paw']}웰스프레쉬\n",
                             f"{Constant.IMOGE['emotion']['paw']}푸드라운지\n"]

                return_string = ''
                for i in range(len(rest_name)):
                    return_string += rest_name[i] + "\'" + date + "\', \'업데이트되지않았습니다\', \'업데이트되지않았습니다\'\n"
                # 초기화 작업

                f.writelines(return_string)

        except Exception as e:
            return GEN.set_text(f"[File-Open-Error #143]파일을 수정하는 중 오류가 발생했습니다.{Constant.IMOGE['emotion']['sad']}\n{e}")

        try:
            s3 = boto3.client('s3')  # 이 부분 해당 버킷 생성 후 적절히 수정 예정
            s3.upload_file(Constant.LOCAL_RESTAURANT_MENU, 'sandol', Constant.RESTAURANT_MENU)

        except Exception as e:
            return GEN.set_text(
                f"[File-Open-Error #124]파일을 저장소에 업로드하는 중 오류가 발생했습니다.{Constant.IMOGE['emotion']['sad']}\n{e}")

        return GEN.set_text(f"파일을 정상적으로 초기화했습니다")
class LastTraffic:  # 교통 관련 클래스
    def __init__(self):

        self.SUBWAY_URL = ["https://map.naver.com/v5/api/transit/subway/stations/455/schedule?lang=ko&stationID=455",
                           "https://map.naver.com/v5/api/transit/subway/stations/11120/schedule?lang=ko&stationID=11120"]

    def real_time_traffic(self):
        context = ""
        header = [f"{Constant.IMOGE['emotion']['walk']}4호선 막차시간입니다\n",
                  f"\n{Constant.IMOGE['emotion']['walk']}수인선 막차시간입니다\n"]
        for iteration in range(len(self.SUBWAY_URL)):
            context += ''.join(header[iteration])
            html = requests.get(self.SUBWAY_URL[iteration])
            soup = BeautifulSoup(html.text, 'html.parser')

            last_arrival_weekday = json.loads(soup.text)['weekdaySchedule']  # 평일 막차
            last_arrival_weekend = json.loads(soup.text)['sundaySchedule']  # 주말 막차
            if iteration == 0:
                weekday_last = lambda sign: [last_arrival_weekday[sign][101 + i] for i in
                                             range(len(last_arrival_weekday[sign]) - 101)][::-1]
                weekend_last = lambda sign: [last_arrival_weekend[sign][85 + i] for i in
                                             range(len(last_arrival_weekend[sign]) - 85)][::-1]

            else:
                weekday_last = lambda sign: [last_arrival_weekday[sign][i] for i in
                                             range(len(last_arrival_weekday[sign]))][::-1]
                weekend_last = lambda sign: [last_arrival_weekend[sign][i] for i in
                                             range(len(last_arrival_weekend[sign]))][::-1]
            # usage : weekend_last('up')
            # 마지막에 있는 열차 10개 정도를 가지고 와서 각 막차 시간 비교
            # 모두 불러오지 않는 이유는 속도 때문
            station = [i['headsign'] for i in weekday_last('up')]  # headsign이 가장 처음으로 나오는 경우의 인덱스를 반환하기 위한 리스트
            station_weekend = [i['headsign'] for i in weekend_last('up')]  # headsign이 가장 처음으로 나오는 경우의 인덱스를 반환하기 위한 리스트
            # 상행선에서의 막차별 역을 저장하는 리스트 (역 중복 가능)

            station2 = [i['headsign'] for i in weekday_last('down')]  # headsign이 가장 처음으로 나오는 경우의 인덱스를 반환하기 위한 리스트
            station_weekend2 = [i['headsign'] for i in
                                weekend_last('down')]  # headsign이 가장 처음으로 나오는 경우의 인덱스를 반환하기 위한 리스트
            # 상행선에서의 막차별 역을 저장하는 리스트 (역 중복 가능)

            find_weekday = station.index
            find_weekend = station_weekend.index

            find_weekday2 = station2.index
            find_weekend2 = station_weekend2.index

            find_arrival_time_up = lambda a: weekday_last('up')[a]["departureTime"][:-3]  # 평일 상행선
            find_arrival_time_down = lambda a: weekday_last('down')[a]["departureTime"][:-3]  # 평일 하행선

            find_arrival_time_up2 = lambda a: weekend_last('up')[a]["departureTime"][:-3]  # 주말 상행선
            find_arrival_time_down2 = lambda a: weekend_last('down')[a]["departureTime"][:-3]  # 주말 하행선

            station_name_up: list = [["당고개", "안산", "노원", "금정", "한성대입구", "사당"], ["왕십리", "죽전", "고색"]]
            station_name_down: list = [["오이도"], ["오이도", "인천"]]

            for arv in (station_name_up[iteration]):
                context += ''.join(f"{arv} - ")
                try:
                    context += ''.join(f"(평일) {find_arrival_time_up(find_weekday(arv))}")
                except Exception as e:
                    pass

                try:
                    context += "".join(f"(휴일) {find_arrival_time_up2(find_weekend(arv))}\n")  # 휴일 시간이 있으면 시간 추가
                except Exception as e:
                    context += "".join("\n")  # 휴일 시간 없으면 개행문자 넣고 pass

            for arv in (station_name_down[iteration]):
                context += ''.join(f"{arv} - ")
                try:
                    context += ''.join(f"(평일) {find_arrival_time_down(find_weekday2(arv))}")
                except Exception:
                    pass

                try:
                    context += "".join(f"(휴일) {find_arrival_time_down2(find_weekend2(arv))}\n")  # 휴일 시간이 있으면 시간 추가
                except Exception:
                    context += "".join("\n")  # 휴일 시간 없으면 개행문자 넣고 pass
        return context[:-1]


class Feedback:
    def __init__(self):
        self.S3 = boto3.resource('s3')
        self.S3_client = boto3.client('s3')
        self.bucket = self.S3.Bucket(Constant.BUCKET_NAME)
        self.data = ""

    def upload_feedback(self):
        self.data = f"[{str(datetime.datetime.today())}] : {self.data}\n"

        try:
            self.bucket.download_file(Constant.LOCAL_FEEDBACK_FILE, Constant.FEEDBACK_FILE)

        except Exception as e:
            return GEN.is_Text(
                f"[File-Open-Error #101] 서버에서 피드백 파일을 불러오는 중 오류가 발생했어요{Constant.IMOGE['emotion']['sad']}\n{e}")

        try:
            with open(Constant.LOCAL_FEEDBACK_FILE, "a", encoding="UTF-8") as f:
                f.writelines(self.data)

        except Exception as e:
            return GEN.is_Text(f"[File-Open-Error #102] 파일을 저장 중 오류가 발생했습니다{Constant.IMOGE['emotion']['sad']}\n{e}")

        try:
            self.S3_client.upload_file(Constant.LOCAL_FEEDBACK_FILE, Constant.BUCKET_NAME, Constant.FEEDBACK_FILE)

        except Exception as e:
            return GEN.is_Text(
                f"[File-Open-Error #103] 파일을 서버에 업로드 하는 중 오류가 발생했습니다{Constant.IMOGE['emotion']['sad']}\n{e}")

        return GEN.is_Text(f"피드백 주셔서 감사해요! 빠른 시일내에 검토 후 적용해볼게요!{Constant.IMOGE['emotion']['love']}")

    def manage_feedback(self, option, token):
        # if token not in list(Constant.SANDOL_ACCESS_ID.values()):
        #     return GEN.set_text(f"피드백을 읽을 권한이 없습니다\n{token}")


        try:
            if option == 2:
                delete_feedback()

            else:
                read_feedback()

        except Exception as e:
            return GEN.set_text(f"error : {e}\n{token}")

    def read_feedback(self):
        try:
            self.bucket.download_file(constant.FEEDBACK_FILE, constant.LOCAL_FEEDBACK_FILE)

        except Exception as e:
            GEN.set_text(f"[File-Open-Error #111] 서버에서 피드백 파일을 불러오는 중 오류가 발생했어요\n{e}")

        try:
            with open(constant.LOCAL_FEEDBACK_FILE, 'r', encoding='UTF-8')as f:
                txt = ''.join(f.readlines())
                return GEN.set_text(txt)

        except Exception as e:
            return GEN.set_text(f"[File-Open-Error #112] 파일을 읽는 중 오류가 발생했습니다\n{e}")

    def delete_feedback(self):
        basic_text = "#feedbacks\n"
        try:
            self.bucket.download_file(constant.FEEDBACK_FILE, constant.LOCAL_FEEDBACK_FILE)
        except Exception as e:
            return GEN.set_text(f"[File-Open-Error #113] 서버에서 피드백 파일을 불러오는 중 오류가 발생했어요\n{e}")

        try:
            with open(constant.LOCAL_FEEDBACK_FILE, 'w', encoding="UTF-8") as f:
                f.writelines(basic_text)

        except Exception as e:
            return GEN.set_text(f"[File-Open-Error #114] 파일 데이터를 삭제 중 오류가 발생했습니다{e}")
        return GEN.set_text("정상적으로 삭제했습니다")
class Covid:
    def __init__(self):
        self.return_string = ""

    def today_covid(self) -> dict:
        try:
            url = 'https://m.search.naver.com/p/csearch/content/nqapirender.nhn?where=nexearch&pkid=9005&key=diffV2API'
            html = requests.get(url).text
            data = json.loads(html)
            result = f"{data['result']['list'][-1]['date']}일까지 코로나 발생현황이에요 {Constant.IMOGE['emotion']['walk']}\n" \
                     f"{Constant.IMOGE['emotion']['paw']}지역발생 : {data['result']['list'][-1]['local']}명\n" \
                     f"{Constant.IMOGE['emotion']['paw']}해외발생 : {data['result']['list'][-1]['oversea']}명 입니다!\n " \
                     f"코로나 조심하세요!{Constant.IMOGE['emotion']['nexpression']}"
            # 결과 컨텍스트

            self.return_string = GEN.set_card(Constant.SANDOL_COVID_IMG, is_title="코로나 확진자 수",
                                              is_description=result)

        except Exception as e:
            description = f"코로나 확진자 정보를 불러오는데 실패했어요{Constant.IMOGE['emotion']['sad']}\n"
            self.return_string = GEN.set_card(Constant.SANDOL_COVID_IMG, is_title=f"{e}", is_description=description)

        finally:
            return self.return_string


class Weather:
    def __init__(self):
        self.URL = 'https://search.naver.com/search.naver?query='
        self.return_string = ''

    def weather(self, location: str = "정왕") -> dict:
        url = self.URL + (location + "날씨")
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        form = soup.find("div", {'class': 'api_subject_bx'}).find("div", {'class': 'main_info'}).find("div", {
            'class': 'info_data'})
        sub_form = soup.find("div", {'class': 'api_subject_bx'}).find("div", {'class': 'sub_info'}).find("div", {
            'class': 'detail_box'})

        today_temp = form.find("span", {'class': 'todaytemp'}).text

        try:
            today_temp_min = form.find("span", {'class': 'min'}).text
        except Exception:
            today_temp_min = "-"

        try:
            today_temp_max = form.find("span", {'class': 'max'}).text
        except Exception():
            today_temp_max = "-"

        try:
            today_temp_ray = form.find("span", {'class': 'indicator'}).find("span").text
        except Exception:
            today_temp_ray = "-"

        update_date = soup.find("div", {'class': 'guide_bx _guideBox'}).find("span", {'class': 'guide_txt'}) \
            .find('span', {'class': 'update'}).text

        today_weather = form.find("ul").find("li").text.strip()  # 날씨 정보
        today_dust_list = sub_form.find_all("dd")  # 미세먼지 폼
        today_dust10 = today_dust_list[0].text.replace("㎥", "㎥, ")  # 미세먼지 정보
        today_dust25 = today_dust_list[1].text.replace("㎥", "㎥, ")  # 초미세먼지 정보

        try:
            weather_icon = Constant.IMOGE['weather'][today_weather.split(', ')[0]]

        except Exception:
            weather_icon = ''

        result = f"{Constant.IMOGE['emotion']['walk']}{location}의 기상정보입니다\n\n" \
                 f"기온 : {today_temp}°C ({today_temp_min}°C / {today_temp_max}°C) {weather_icon}\n" \
                 f"미세먼지 : {today_dust10}\n" \
                 f"초미세먼지 : {today_dust25}\n" \
                 f"자외선 : {today_temp_ray}이에요!\n\n" \
                 f"{update_date}시에 업데이트된 네이버 날씨 정보입니다!"

        return GEN.set_text(result)


class Announcement:
    def __init__(self):
        self.URL = "http://www.kpu.ac.kr/front/boardlist.do?bbsConfigFK=1&siteGubun=14&menuGubun=1"
        self.ORIGIN = "http://www.kpu.ac.kr"
        self.TITLE = "교내 최신 학사공지 내역입니다"
        self.MAX_ANNOUNCEMENT_CNT = 5  # 최대 가져올 공지 수
        self.webLinkUrl = "http://www.kpu.ac.kr/contents/main/cor/noticehaksa.html"

    def announce(self) -> dict:
        req = requests.get(self.URL)
        soup = BeautifulSoup(req.text, 'html.parser')
        announce_list = soup.find('table').find('tbody').find_all('tr')
        result = []  # title, date, URl

        for i in range(self.MAX_ANNOUNCEMENT_CNT):
            result.append([announce_list[i].find_all("td")[1].find('a').text.strip(),
                           announce_list[i].find_all("td")[4].text.strip(),
                           self.ORIGIN + announce_list[i].find_all("td")[1].find("a")['href']])

        return GEN.set_list(self.TITLE, result,
                            is_Button=GEN_OPTION.Button(label="바로가기", action="weblink", weblinkUrl=self.webLinkUrl))


class LiveSubwayTraffic:
    def __init__(self, station_no: str = ["455", "11120"]) -> None:
        self.URL = "https://map.naver.com/v5/api/transit/subway/stations/"
        self.time = None
        self.station_name: str
        self.return_data = ''
        self.station_no = station_no

    def get_data(self) -> dict:
        URL = self.URL + self.station_no + "/schedule?lang=ko&stationID=" + self.station_no
        html = requests.get(URL).text
        soup = BeautifulSoup(html, 'html.parser')

        json_data = json.loads(soup.text)
        # print(json_data)
        return json_data

    def arrival_time(self):
        try:
            if self.data['todayServiceDay']['name'] == '평일':  # 평일 시간표
                schedule_data_up = self.data['weekdaySchedule']['up']
                schedule_data_down = self.data['weekdaySchedule']['down']

                it = schedule_data_up.__iter__()  # 상행선
                flag = False
                for i in schedule_data_up:
                    it.__next__()
                    if datetime.datetime.strptime(i['departureTime'], '%H:%M:%S') > self.time:
                        self.return_data += i['headsign'] + " 방면 " + i['departureTime'] + ", "\
                                            + it.__next__()['departureTime'] + "\n"
                        flag = True
                        break
                    else:
                        continue

                if flag == False:
                    self.return_data += schedule_data_up[-1]['headsign'] + schedule_data_up[-1]['departureTime'] + " 막차입니다"

                self.return_data += "\n\n"

                flag = False
                it = schedule_data_down.__iter__()  # 하행선
                for i in schedule_data_down:
                    it.__next__()
                    if datetime.datetime.strptime(i['departureTime'], '%H:%M:%S') > self.time:
                        self.return_data += i['headsign'] + "방면 " + i['departureTime'] + ", " \
                                            + it.__next__()['departureTime'] + "\n"
                        flag = True
                        # print(i['departureTime'], end=' ')
                        # print(it.__next__()['departureTime'], end=' ')
                        break

                    else:
                        continue

                if flag == False:
                    self.return_data += schedule_data_down[-1]['headsign'] + schedule_data_down[-1][
                        'departureTime'] + " 막차입니다"

            else:  # 주말 시간표
                schedule_data_up = self.data['sundaySchedule']['up']
                schedule_data_down = self.data['sundaySchedule']['down']

                flag = False

                it = schedule_data_up.__iter__()
                for i in schedule_data_up:
                    it.__next__()
                    if datetime.datetime.strptime(i['departureTime'], '%H:%M:%S') > self.time:
                        self.return_data += i['headsign'] + "방면 " + i['departureTime'] + ", " \
                                            + it.__next__()['departureTime'] + "\n"
                        flag = True
                        # print(i['departureTime'], end=' ')
                        # print(it.__next__()['departureTime'])
                        break

                    else:
                        continue

                if flag == False:
                    self.return_data += schedule_data_up[-1]['headsign'] + schedule_data_up[-1]['departureTime'] + " 막차입니다"

                flag = False
                it = schedule_data_down.__iter__()
                for i in schedule_data_down:
                    it.__next__()
                    if datetime.datetime.strptime(i['departureTime'], '%H:%M:%S') > self.time:
                        self.return_data += i['headsign'] + "방면 " + i['departureTime'] + ", " \
                                            + it.__next__()['departureTime'] + "\n"
                        flag = True
                        # print(i['departureTime'], end=' ')
                        # print(it.__next__()['departureTime'])
                        break

                    else:
                        continue

                if flag == False:
                    self.return_data += schedule_data_down[-1]['headsign'] + schedule_data_down[-1][
                        'departureTime'] + " 막차입니다"

        except Exception as e:
            return str(e)


    def get_time(self) -> dict:
        return gen.set_text(self.time)

    def get_string(self, time):
        self.time = datetime.datetime.strptime(time, '%H:%M:%S')  # time 모듈로 변환
        for subway in self.station_no:
            self.station_no = subway
            self.data = self.get_data()
            self.arrival_time()
        return self.return_data



class Test:  # 테스트 블럭이 참조할 클래스 (직접 테스트해야하는경우에 해당 클래스에 작성 후 테스트 발화시 결과 나옴.)
    def __init__(self):
        pass
