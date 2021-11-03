import requests
import json
import alphaSandol as settings


class Covid:
    def __init__(self):
        self.return_string = ""

    def today_covid(self) -> dict:
        try:
            url = 'https://m.search.naver.com/p/csearch/content/nqapirender.nhn?where=nexearch&pkid=9005&key=diffV2API'
            html = requests.get(url).text
            data = json.loads(html)
            result = f"{data['result']['list'][-1]['date']}일까지 코로나 발생현황이에요 {settings.IMOGE('emotion', 'walk')}\n" \
                     f"{settings.IMOGE('emotion', 'paw')}지역발생 : {data['result']['list'][-1]['local']}명\n" \
                     f"{settings.IMOGE('emotion', 'paw')}해외발생 : {data['result']['list'][-1]['oversea']}명 입니다!\n " \
                     f"코로나 조심하세요!{settings.IMOGE('emotion', 'nexpression')}"
            # 결과 컨텍스트

            self.return_string = settings.GEN.set_card(settings.SANDOL_COVID_IMG, is_title="코로나 확진자 수",
                                                       is_description=result)

        except Exception as e:
            description = f"코로나 확진자 정보를 불러오는데 실패했어요{settings.IMOGE('emotion', 'sad')}\n"
            self.return_string = settings.GEN.set_card(settings.SANDOL_COVID_IMG, is_title=f"{e}",
                                                       is_description=description)

        finally:
            return self.return_string


if __name__ == "__main__":
    print(Covid().today_covid())