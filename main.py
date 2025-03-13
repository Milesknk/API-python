from fastapi import FastAPI 
import mysql.connector
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from pydicom import dcmread
import time
import datetime
import ast


def FindTagDicom(dataSet,dataTag):
    if dataTag in dataSet:
        print(f"|-{dataTag} = " + str(dataSet[dataTag].value))
    else :
        pass

def Waveform(ds,index):
    
    print("\n----------------------------")
    print("ds.WaveformSequence["+ str(index)+ "]")
    if "WaveformSequence" in ds:
        
        #print(" len(ds.WaveformSequence) 72 = ", len(ds.WaveformSequence))
        #print("index 74 = ",index)

        if index >= 0 and index < len(ds.WaveformSequence):
            ex = ds.WaveformSequence[index]
            FindTagDicom(ex,"SamplingFrequency")
            FindTagDicom(ex,"MultiplexGroupLabel")
            FindTagDicom(ex,"WaveformBitsAllocated")
            FindTagDicom(ex,"WaveformSampleInterpretation")
        else :
            pass
            #print("Index out of range")
    else :
        print("No WaveformSequence")
    print("\n----------------------------")


app = FastAPI()


@app.get("/")
def read_root():
    return { "message" : "Hi root"}

def get_db_connector():
    mydb = mysql.connector.connect(
        host="172.16.0.45",
        user="webmaster",
        password="mutdb123456",
        database="ECG_MNG"
        )
    return mydb



@app.get("/wf/{DocId}")
def get_wf(DocId: str):
    mydb = get_db_connector()
    mycursor = mydb.cursor()

    query = "SELECT * FROM Waveform_Info WHERE DocId = %s"
    mycursor.execute(query, (DocId,))

    row = mycursor.fetchone()

    mycursor.close()
    mydb.close()

    if not row:
        return {"message": "DocId not found"}

    # Return a single dictionary, not a list
    
    data = {

            "RootPath": row[3]
        }
    
    root_path = data["RootPath"]

    path = f"{root_path}"

    for a in range(0,len(path)):
        pathx = (path)
        print("\n----------------------------")
        print('pathx : ' + pathx)
        time.sleep(5)
        
        ds = dcmread(pathx)
        if "WaveformSequence" in ds:
            multipleWaveform = ds.WaveformSequence[a]
        else :
            print("No WaveformSequence")
        #print(multipleWaveform)
        #print(ds)

        dt = datetime.datetime.now()
        CreateDate = (dt.strftime("%d/%m/%Y"))
        CreateTime = (dt.strftime("%H:%M:%S"))
        print("CreateDate", CreateDate, "CreateTime",CreateTime)

        if "WaveformAnnotationSequence" in ds:
            if len(ds.WaveformAnnotationSequence) == 0:
                multipleWaveformAnnotation = "" 
            else:
                multipleWaveformAnnotation = ds.WaveformAnnotationSequence
        else:
            multipleWaveformAnnotation = ""
            print("false(multipleWaveformAnnotation)")    
        x = len(multipleWaveform.ChannelDefinitionSequence)
        
        
        if "AcquisitionContextSequence" in ds:
            if len(ds.AcquisitionContextSequence) == 0:
                multipleAcquisitionContext = "" 
            else:
                multipleAcquisitionContext = ds.AcquisitionContextSequence[0] 
        else:
            multipleAcquisitionContext = ""

        print("----- Read Data ----- 21")

        print("length waveform = " + str(len(multipleWaveform)))
        print("length multipleWaveform.ChannelDefinitionSequence = " + str(len(multipleWaveform.ChannelDefinitionSequence)))
        #print(multipleWaveform_item)

        print("\n------------------------------------")
        print("-    Patient Data                  -")
        print("------------------------------------")
        print("Patient Id = " + ds.PatientID)
        print("Patient Name = " + str(ds.PatientName))
        print("PatientBirthDate = " + str(ds.PatientBirthDate))
        print("PatientSex = " + str(ds.PatientSex))
        print("PatientAge = " + str(ds.PatientAge))
        wfValue2 = (ds.PatientID) 

        print("\n------------------------------------")
        print("-    Study Data                  -")
        print("------------------------------------")
        print("Study Date = " + str(ds.StudyDate))
        print("Study Time = " + str(ds.StudyTime))

        print("\n------------------------------------")
        print("-    ds.WaveformSequence[0]         -")
        print("------------------------------------")
        
        Waveform(ds, 0)
        Waveform(ds, 1)
        
        print("------------------------------------")
        print("175 multipleWaveform len = " + str(len(multipleWaveform)))

        print("\nWaveformSequence +++")
        

        
        for i in range(0,len(multipleWaveform)):

            print("\n+++ " + str(i) + " +++")
            FindTagDicom(multipleWaveform,"MultiplexGroupTimeOffset")
            FindTagDicom(multipleWaveform,"TriggerTimeOffset")
        
            try :
                print(" |-TriggerSamplePosition = " + str(multipleWaveform.TriggerSamplePosition))
            except:
                pass
            
            FindTagDicom(multipleWaveform,"NumberOfWaveformChannels") 
            FindTagDicom(multipleWaveform,"NumberOfWaveformSamples") 
            FindTagDicom(multipleWaveform,"WaveformOriginality")
            print("|-WaveformData Len = " + str(len(multipleWaveform.WaveformData)))
            
        print("------------------------------------")
        
        for i in range(0,x):

            multipleWaveform_item = multipleWaveform.ChannelDefinitionSequence[i]
        
            print("\n+++ " + str(i) + " +++")
            
            print(" |-ChannelSensitivityUnitsSequence")
            seTagDicom = multipleWaveform_item.ChannelSensitivityUnitsSequence[0]
            FindTagDicom(seTagDicom,"CodeValue")
            FindTagDicom(seTagDicom,"CodingSchemeDesignator")
            FindTagDicom(seTagDicom,"CodingSchemeVersion")
            FindTagDicom(seTagDicom,"CodeMeaning")
            print(" |-ChannelDefinitionSequence")
            soTagDicom = multipleWaveform_item.ChannelSourceSequence[0]
            FindTagDicom(soTagDicom,"CodeValue")
            FindTagDicom(soTagDicom,"CodingSchemeDesignator")
            FindTagDicom(soTagDicom,"CodingSchemeVersion")
            FindTagDicom(soTagDicom,"CodeMeaning")
        #i = 96
        #    print("ChannelSensitivity = " + str(multipleWaveform_item[i].ChannelSensitivity))
        #print("mult_AnnotationItem =" + str(multipleWaveformAnnotation[i].ReferencedWaveformChannels))

        
        print("SamplingFrequency = " + str(multipleWaveform.SamplingFrequency))
        print("ChannelSensitivity = " + str(multipleWaveform_item.ChannelSensitivity))
        print("CodeMeaning = " + str(multipleWaveform_item.ChannelSensitivityUnitsSequence[0].CodeMeaning))

        print("\n -- WaveformAnnotation --")
        print("len(multipleWaveformAnnotation) = " + str(len(multipleWaveformAnnotation)))
        AnnotationArraydata = []

        if len(multipleWaveformAnnotation) > 0:
            for f in range (0,(len(multipleWaveformAnnotation))):
                multi_itemAnnotation = multipleWaveformAnnotation[f]
                #FindTagDicom(itemconcept.ConceptNameCodeSequence[0],"CodeMeaning")
                print ("\n+++ " + str(f) + " +++")
                if hasattr(multi_itemAnnotation, "ConceptNameCodeSequence"):
                    ConceptTagDicom = multi_itemAnnotation.ConceptNameCodeSequence[0]
                    print("\nConceptNameCodeSequence.CodeMeaning")
                    FindTagDicom(ConceptTagDicom, "CodeMeaning")
                else:
                    pass

                if hasattr(multi_itemAnnotation, "MeasurementUnitsCodeSequence"):
                    MeasurementUnitsTagDicom = multi_itemAnnotation.MeasurementUnitsCodeSequence[0]
                    print("\nMeasurementUnitsCodeSequence.CodeMeaning")
                    FindTagDicom(MeasurementUnitsTagDicom,"CodeMeaning")
                else:
                    pass
                if hasattr(multi_itemAnnotation, "NumericValue"):
                    Numericdata = multi_itemAnnotation["NumericValue"].value
                    print(str(Numericdata))
                    AnnotationArraydata.append(Numericdata)
                else:
                    pass
                if hasattr(multi_itemAnnotation, "ReferencedSamplePositions"):
                    RefSampdata = multi_itemAnnotation["ReferencedSamplePositions"].value
                    print(str(RefSampdata))
                    AnnotationArraydata.append(RefSampdata)
                else:
                    pass

                if "ConceptNameCodeSequence" in multipleWaveformAnnotation[f]:
                    multipleWaveformAnnotation_concept = multipleWaveformAnnotation[f].ConceptNameCodeSequence
                    print("\nmultipleWaveformAnnotation_concept = " , multipleWaveformAnnotation_concept)

                else:
                    pass
                if "ConceptNameCodeSequence" in multipleWaveformAnnotation[f]:
                    multipleWaveformAnnotation_Measurement = multipleWaveformAnnotation[f].ConceptNameCodeSequence
                    print("\nmultipleWaveformAnnotation_Measurement = ",multipleWaveformAnnotation_Measurement)

                else:
                    pass
        #for xx in range (0,len(multipleWaveformAnnotation.ConceptNameCodeSequence)):
        print("331 AnnotationArraydata",AnnotationArraydata)
        print("ECG --- Waveform")
        
        try :
            multiplex_1 = ds.waveform_array(a)
        except:
            pass
        
        print(multiplex_1.shape)
        lead_Value = []
        newLead = []
        for i in range(0,12):
        
            print("--------" + str(i) +"-------")
            wfdataxx = []
            finalresult = []
            for j in range (0,min(5000, len(multiplex_1))):
                gg = str(multiplex_1[j][i])
                tt = gg.split(".")
                tt[1] = tt[1][0:2]
                newtext = '.'.join(tt)
                wfdataxx.append(newtext)

            for data in wfdataxx:
                
                finalresult.append(str(data))
                
            lead_Value.append(finalresult)
            #print(len(lead_Value))

            new_string = ','.join(lead_Value[i])
            newLead.append(new_string)
        
        #print("newLead", newLead)
        #print("len newLead", len(newLead))

        #xxx = ['123', '456', '789']
        #new_string = ','.join(xxx)
        #Replace ', ' (comma followed by space) with just a comma
        #print("xxx = ",xxx)
        #print("new_string = ",new_string)
        
        newLead.append(wfValue2)
        if (len(AnnotationArraydata) > 0):
            newLead.append(AnnotationArraydata)
        else:
            pass
        tupleLead = tuple(newLead)
        print("newLead",len(newLead))

        #print ("ff['Lead_I'] = " , lead_values_dict['Lead_I'])
        #print ("ff['Lead_II'] = " , lead_values_dict['Lead_II'])
        #print ("ff",lead_values_dict)
        
        #dict version
        #print ("331" , type(lead_values_dict))
        Annotat_data = []
        #Annotat_data = newLead[13].split(",")
        print(len(AnnotationArraydata))
        data = {
            "id": row[0],
            "PatientId": newLead[12],
            "Lead_I": newLead[0],
            "Lead_II": newLead[1],
            "Lead_III": newLead[2],
            "Lead_aVR": newLead[3],
            "Lead_aVL": newLead[4],
            "Lead_aVF": newLead[5],
            "Lead_V1": newLead[6],
            "Lead_V2": newLead[7],
            "Lead_V3": newLead[8],
            "Lead_V4": newLead[9],
            "Lead_V5": newLead[10],
            "Lead_V6": newLead[11],
            "PR Interval": AnnotationArraydata[0],
            "QRS Duration": AnnotationArraydata[1],
            "QT Interval": AnnotationArraydata[2],
            "QTc Interval": AnnotationArraydata[3],
            "P Axis": AnnotationArraydata[4],
            "QRS Axis": AnnotationArraydata[5],
            "T Axis": AnnotationArraydata[6],
            "P onset": AnnotationArraydata[7],
            "P offset": AnnotationArraydata[8],
            "QRS onset": AnnotationArraydata[9],
            "QRS offset": AnnotationArraydata[10],
            "T offset": AnnotationArraydata[11]

        }

        return data

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any domain (frontend). If you want to allow only specific domains, use ["http://localhost:3000", "https://myfrontend.com"] instead.
    #allow_credentials=True, #Allows sending cookies or authentication tokens (e.g., JWT, session tokens).
    #allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE)
    #allow_headers=["*"], #Allows all HTTP headers (e.g., Authorization, Content-Type). You can also allow specific headers, like ["Authorization", "Content-Type"].
) 
