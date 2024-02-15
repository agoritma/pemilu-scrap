import aiohttp
import asyncio
import json
import os

URL_PROV = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/0.json"
BASE_URL_WILAYAH = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp/"
BASE_URL_TPS = "https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp/"
WEB_URL = "https://pemilu2024.kpu.go.id/pilpres/hitung-suara"

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
                    pass
                else:
                    namaProv = prov["nama"]
                    kodeProv = prov["kode"]
                    await asyncio.create_task(kotaListReq(session, kodeProv, namaProv))
            
async def kotaListReq(session, kodeProv, namaProv):
    async with session.get(BASE_URL_WILAYAH+kodeProv+".json") as reqKota:
        dataKota = await reqKota.json()
        for kota in dataKota:
            namaKota = kota["nama"]
            kodeKota = kota["kode"]
            makeDir(f'{namaProv}/{namaKota}')
            await asyncio.create_task(kecListReq(session, kodeProv, kodeKota, namaProv, namaKota))
        
async def kecListReq(session, kodeProv, kodeKota, namaProv, namaKota):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}'+".json") as reqKec:
        dataKec = await reqKec.json()
        for kec in dataKec:
            namaKec = kec["nama"]
            kodeKec = kec["kode"]
            makeDir(f'{namaProv}/{namaKota}/{namaKota}')
            await asyncio.create_task(kelListReq(session, kodeProv, kodeKota, kodeKec, namaProv, namaKota, namaKec))
        
async def kelListReq(session, kodeProv, kodeKota, kodeKec, namaProv, namaKota, namaKec):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}/{kodeKec}'+".json") as reqKel:
        dataKel= await reqKel.json()
        for kel in dataKel:    
            namaKel = kel["nama"]
            print(namaKel)
            kodeKel = kel["kode"]
            makeDir(f'{namaProv}/{namaKota}/{namaKota}/{namaKec}')
            await asyncio.create_task(tpsListReq(session, kodeProv, kodeKota, kodeKec, kodeKel, namaProv, namaKota, namaKec, namaKel))
        
async def tpsListReq(session, kodeProv, kodeKota, kodeKec, kodeKel, namaProv, namaKota, namaKec, namaKel):
    async with session.get(BASE_URL_WILAYAH+f'{kodeProv}/{kodeKota}/{kodeKec}/{kodeKel}'+".json") as reqTPS:
        listTPS = await reqTPS.json()
        for tps in listTPS:
            namaTPS = tps["nama"]
            print(namaTPS)
            kodeTPS = tps["kode"]
            makeDir(f'{namaProv}/{namaKota}/{namaKota}/{namaKec}/{namaKel}')
            await asyncio.create_task(tpsDataReq(session, kodeProv, kodeKota, kodeKec, kodeKel, kodeTPS, namaTPS))
        
async def tpsDataReq(session, kodeProv, kodeKota, kodeKec, kodeKel, kodeTPS, namaTPS):
    tpsID = f'{kodeProv}/{kodeKota}/{kodeKec}/{kodeKel}/{kodeTPS}'
    async with session.get(BASE_URL_TPS+tpsID+".json") as reqDataTPS:
        dataTPS = await reqDataTPS.json()
        if (dataTPS["chart"] != None):
            dataTPS["chart"] = {
                "01": dataTPS["chart"]["100025"],
                "02": dataTPS["chart"]["100026"],
                "03": dataTPS["chart"]["100027"]
            }
        return {
            "urlTPS": WEB_URL+"/"+tpsID,
            "namaProv": "",
            "namaKota": "",
            "namaKec": "",
            "namaKel": "",
            "namaTPS": namaTPS,
            "kodeTPS": kodeTPS,
            "dataTPS": dataTPS
        }
        
if __name__ == "__main__":
    asyncio.run(main())