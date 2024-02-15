import aiohttp
import asyncio
import json
import os
import pandas as pd

URL_PROV = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/0.json"
BASE_URL_WILAYAH = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/"
BASE_URL_TPS = "https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"
WEB_URL = "https://pemilu2024.kpu.go.id/pilpres/hitung-suara"

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
            for prov in dataProv[checkPoint["provIndex"]:]:
                if (prov["nama"] == "Luar Negeri"):
                    checkPoint["provIndex"] += checkPoint["provIndex"]+1
                    checkPointUpdate(checkPoint)
                    pass
                else:
                    namaProv = prov["nama"]
                    kodeProv = prov["kode"]
                    await asyncio.create_task(kotaListReq(session, kodeProv, namaProv))
                    checkPoint["provIndex"] = checkPoint["provIndex"]+1
                    checkPointUpdate(checkPoint)
                checkPoint["provIndex"] = 0
                checkPointUpdate(checkPoint)
            
async def kotaListReq(session, kodeProv, namaProv):
    async with session.get(BASE_URL_WILAYAH+kodeProv+".json") as reqKota:
        dataKota = await reqKota.json()
        checkPoint["kotaIndex"] = 0
        checkPointUpdate(checkPoint)
        for kota in dataKota[checkPoint["kotaIndex"]:]:
            namaKota = kota["nama"]
            kodeKota = kota["kode"]
            makeDir(f'{namaProv}/{namaKota}')
            await asyncio.create_task(kecListReq(session, kodeProv, kodeKota, namaProv, namaKota))
            checkPoint["kotaIndex"] = checkPoint["kotaIndex"]+1
            checkPointUpdate(checkPoint)
        checkPoint["kotaIndex"] = 0
        checkPointUpdate(checkPoint)
        
async def kecListReq(session, kodeProv, kodeKota, namaProv, namaKota):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}'+".json") as reqKec:
        dataKec = await reqKec.json()
        checkPoint["kecIndex"] = 0
        checkPointUpdate(checkPoint)
        for kec in dataKec[checkPoint["kecIndex"]:]:
            namaKec = kec["nama"]
            kodeKec = kec["kode"]
            makeDir(f'{namaProv}/{namaKota}')
            await asyncio.create_task(kelListReq(session, kodeProv, kodeKota, kodeKec, namaProv, namaKota, namaKec))
            checkPoint["kecIndex"] = checkPoint["kecIndex"]+1
            checkPointUpdate(checkPoint)
        checkPoint["kecIndex"] = 0
        checkPointUpdate(checkPoint)
        
async def kelListReq(session, kodeProv, kodeKota, kodeKec, namaProv, namaKota, namaKec):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}/{kodeKec}'+".json") as reqKel:
        dataKel= await reqKel.json()
        for kel in dataKel[checkPoint["kelIndex"]:]:
            namaKel = kel["nama"]
            kodeKel = kel["kode"]
            makeDir(f'{namaProv}/{namaKota}/{namaKec}')
            await asyncio.create_task(tpsListReq(session, kodeProv, kodeKota, kodeKec, kodeKel, namaProv, namaKota, namaKec, namaKel))
            checkPoint["kelIndex"] = checkPoint["kelIndex"]+1
            checkPointUpdate(checkPoint)
        checkPoint["kelIndex"] = 0
        checkPointUpdate(checkPoint)
        
async def tpsListReq(session, kodeProv, kodeKota, kodeKec, kodeKel, namaProv, namaKota, namaKec, namaKel):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}/{kodeKec}/{kodeKel}'+".json") as reqTPS:
        listTPS = await reqTPS.json()
        for tps in listTPS:
            namaTPS = tps["nama"]
            kodeTPS = tps["kode"]
            makeDir(f'{namaProv}/{namaKota}/{namaKec}/{namaKel}')
            await asyncio.create_task(tpsDataReq(session, kodeProv, kodeKota, kodeKec, kodeKel, kodeTPS, namaProv, namaKota, namaKec, namaKel, namaTPS))
        
async def tpsDataReq(session, kodeProv, kodeKota, kodeKec, kodeKel, kodeTPS, namaProv, namaKota, namaKec, namaKel, namaTPS):
    tpsID = f'{kodeProv}/{kodeKota}/{kodeKec}/{kodeKel}/{kodeTPS}'
    async with session.get(BASE_URL_TPS+tpsID+".json") as reqDataTPS:
        dir = f'{namaProv}/{namaKota}/{namaKec}/{namaKel}'
        dataTPS = await reqDataTPS.json()
        print('> ' + dir + "/" + namaTPS)
        
        if (dataTPS["chart"] != None):
            dataTPS["chart"] = {
                "01": dataTPS["chart"]["100025"],
                "02": dataTPS["chart"]["100026"],
                "03": dataTPS["chart"]["100027"]
            }
        
        jsonData = {
            "urlTPS": WEB_URL+"/"+tpsID,
            "namaProv": namaProv,
            "namaKota": namaKota,
            "namaKec": namaKec,
            "namaKel": namaKel,
            "namaTPS": namaTPS,
            "kodeTPS": kodeTPS,
            "dataTPS": dataTPS
        }
        
        df = pd.DataFrame([jsonData])
        
        df.to_csv(f'{dir}/{namaTPS}.csv', index=False)
        
        with open(f'{dir}/{namaTPS}.json', "w") as f:
            f.write(json.dumps(jsonData, indent=4))
        
if __name__ == "__main__":
    asyncio.run(main())