import aiohttp
import asyncio
import json
import os
import pandas as pd
from datetime import datetime

URL_PROV = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/0.json"
BASE_URL_WILAYAH = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/"
BASE_URL_TPS = "https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"
WEB_URL = "https://pemilu2024.kpu.go.id/pilpres/hitung-suara"

timeStamp = datetime.now()

with open("checkpoint.json", "r") as f:
    checkPoint = json.load(fp=f)

def checkPointUpdate(data):
    with open("checkpoint.json", "w") as f:
        f.write(json.dumps(data, indent=4))

def makeDir(dir):
    folders = ""
    for folder in dir.split("/"):
        folders += folder+"/"
        try:
            os.mkdir(folders)
        except FileExistsError:
            pass
    return True

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_PROV) as reqProv:
            dataProv = await reqProv.json()
            for prov in dataProv:
                if (prov["nama"] == "Luar Negeri"):
                    checkPoint["provIndex"] += 1
                    checkPointUpdate(checkPoint)
                    pass
                else:
                    namaProv = prov["nama"]
                    kodeProv = prov["kode"]
                    await asyncio.ensure_future(kotaListReq(session, kodeProv, namaProv))
            
async def kotaListReq(session, kodeProv, namaProv):
    async with session.get(BASE_URL_WILAYAH+kodeProv+".json") as reqKota:
        dataKota = await reqKota.json()
        listProvTask = []
        for kota in dataKota:
            namaKota = kota["nama"]
            kodeKota = kota["kode"]
            makeDir(f'{timeStamp}/{namaProv}/{namaKota}')
            listProvTask.append(asyncio.ensure_future(kecListReq(session, kodeProv, kodeKota, namaProv, namaKota)))
        listProvResult = await asyncio.gather(*listProvTask)
        
async def kecListReq(session, kodeProv, kodeKota, namaProv, namaKota):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}'+".json") as reqKec:
        dataKec = await reqKec.json()
        listKotaTask = []
        for kec in dataKec:
            namaKec = kec["nama"]
            kodeKec = kec["kode"]
            makeDir(f'{timeStamp}/{namaProv}/{namaKota}')
            listKotaTask.append(asyncio.ensure_future(kelListReq(session, kodeProv, kodeKota, kodeKec, namaProv, namaKota, namaKec)))
        listKotaResult = await asyncio.gather(*listKotaTask)
        
async def kelListReq(session, kodeProv, kodeKota, kodeKec, namaProv, namaKota, namaKec):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}/{kodeKec}'+".json") as reqKel:
        dataKel = await reqKel.json()
        listKecTask = []
        for kel in dataKel:
            namaKel = kel["nama"]
            kodeKel = kel["kode"]
            makeDir(f'{timeStamp}/{namaProv}/{namaKota}/{namaKec}')
            listKecTask.append(asyncio.ensure_future(tpsListReq(session, kodeProv, kodeKota, kodeKec, kodeKel, namaProv, namaKota, namaKec, namaKel)))
            checkPoint["kelIndex"] += 1
        dataListKecResult = await asyncio.gather(*listKecTask)
        
async def tpsListReq(session, kodeProv, kodeKota, kodeKec, kodeKel, namaProv, namaKota, namaKec, namaKel):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}/{kodeKec}/{kodeKel}'+".json") as reqTPS:
        dir = f'{timeStamp}/{namaProv}/{namaKota}/{namaKec}'
        listTPS = await reqTPS.json()
        dataListKel = []
        listKelTask = []
        for tps in listTPS:
            namaTPS = tps["nama"]
            kodeTPS = tps["kode"]
            makeDir(f'{timeStamp}/{namaProv}/{namaKota}/{namaKec}')
            listKelTask.append(asyncio.ensure_future(tpsDataReq(session, kodeProv, kodeKota, kodeKec, kodeKel, kodeTPS, namaProv, namaKota, namaKec, namaKel, namaTPS)))
        dataListKelResult = await asyncio.gather(*listKelTask)
        dataListKel = list(dataListKelResult)
        df = pd.DataFrame(dataListKel)
        namaFile = str(namaKel).replace("/", "Atau")
        df.to_csv(f'{dir}/{namaFile}.csv', index=False)
            
async def tpsDataReq(session, kodeProv, kodeKota, kodeKec, kodeKel, kodeTPS, namaProv, namaKota, namaKec, namaKel, namaTPS):
    tpsID = f'{kodeProv}/{kodeKota}/{kodeKec}/{kodeKel}/{kodeTPS}'
    async with session.get(BASE_URL_TPS+tpsID+".json") as reqDataTPS:
        dir = f'{timeStamp}/{namaProv}/{namaKota}/{namaKec}/{namaKel}'
        resp = await reqDataTPS.read()
        dataTPS = json.loads(resp)
        print('[+] ' + dir + "/" + namaTPS)
        
        if (dataTPS["chart"] != None):
            try:
                calon = {
                    "suara_01": dataTPS["chart"]["100025"],
                    "suara_02": dataTPS["chart"]["100026"],
                    "suara_03": dataTPS["chart"]["100027"]
                }
            except KeyError:
                calon = {
                "suara_01": 0,
                "suara_02": 0,
                "suara_03": 0
            }
        else:
            calon = {
                "suara_01": 0,
                "suara_02": 0,
                "suara_03": 0
            }
        
        finalData = {
            "urlTPS": WEB_URL+"/"+tpsID,
            "namaProv": namaProv,
            "namaKota": namaKota,
            "namaKec": namaKec,
            "namaKel": namaKel,
            "namaTPS": namaTPS,
            "kodeTPS": kodeTPS
        }
        
        finalData.update(calon)
        if dataTPS["administrasi"] != None:
            finalData.update(dataTPS["administrasi"])
        if dataTPS["psu"] != None:
            finalData.update({"psu": dataTPS["psu"]})
        finalData.update({
            "status_adm": dataTPS["status_adm"],
            "status_suara": dataTPS["status_suara"],
            "update_time": dataTPS["ts"]
        })
        
        return finalData
        
if __name__ == "__main__":
    asyncio.run(main())