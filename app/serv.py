import json
import WMF
import time

data_default = {"Purchase":{"UUID":"123-456","TimeOutInMs":30000,"Date":"20240101","Time":"111335000","UnixEpochTimeInMs":1555586015000,"MachineID":1,"MessageType":4,"MessageTypeName":"CREDIT_DENY","ErrorNumbers":[0],"Order":{"BarcodeKey":"0","Product":[{"PLU":5,"RcpNumber":5,"RcpName":"DEFAULT","Price":0.0,"Currency":"EUR","SML":"S","Quantity":1,"Notification":"DEFAULT","TransactionStatusCode":1,"TransactionStatusName":"ACCEPTED"}]}}}
pubMsg_default = {"UUID":"123-123","MachineID":1,"Error":[0],"idError":0,"MessageType":4,"MessageTypeName":"CREDIT_DENY","PLU":0,"RcpNumber":0,"RcpName":"DEFAULT","TransactionStatusCode":2,"TransactionStatusName":"DENIED"}

class pubMsg:
    def __init__(self, data):
        self.UUID = data["UUID"]
        self.MachineID = data["MachineID"]
        self.Error = data["Error"]
        self.idError = data["idError"]
        self.MessageType  = data["MessageType"]
        self.MessageTypeName = data["MessageTypeName"]
        self.PLU = data["PLU"]
        self.RcpNumber = data["RcpNumber"]
        self.RcpName = data["RcpName"]
        self.TransactionStatusCode = data["TransactionStatusCode"]
        self.TransactionStatusName = data["TransactionStatusName"]

    def toJson(self):
        return json.dumps(self.__dict__)

class subMsg:
    def __init__(self, data):
        self.UUID  = data["UUID"]
        self.MachineID  = data["MachineID"]
        self.MessageType = data["MessageType"]
        self.MessageTypeName = data["MessageTypeName"]
        self.Notification = data["Notification"]
        self.TransactionStatusCode = data["TransactionStatusCode"]
        self.TransactionStatusName = data["TransactionStatusName"]
        self.RcpNumber = data["RcpNumber"]
        self.PLU = data["PLU"]
        self.RcpName = data["RcpName"]
    def toJson(self):
        return json.dumps(self.__dict__)


def fromWMF(msg: WMF.Purchase):
    out = pubMsg(pubMsg_default)
    Order = msg.Order
    Product = Order.Products[0]
    out.MessageTypeName = msg.MessageTypeName
    out.MessageType = msg.MessageType
    out.MachineID = msg.MachineID
    out.UUID = msg.UUID
    out.Error = msg.ErrorNumbers
    out.PLU = Product.PLU
    out.RcpNumber = Product.RcpNumber
    out.RcpName = Product.RcpName
    out.TransactionStatusName = Product.TransactionStatusName
    out.TransactionStatusCode = Product.TransactionStatusCode
    return out


def toWMF(msg: subMsg):
    purchase = WMF.Purchase(data_default)
    Order = purchase.Order
    Product = Order.Products[0]
    purchase.UUID = msg.UUID
    purchase.MachineID = msg.MachineID
    purchase.MessageType = msg.MessageType
    purchase.MessageTypeName = msg.MessageTypeName
    Product.Notification = msg.Notification
    purchase.Date = time.strftime("%Y%m%d")
    purchase.Time = time.strftime("%H%M%S000")
    purchase.UnixEpochTimeInMs = int(time.time())
    Product.RcpName = msg.RcpName
    Product.RcpNumber = msg.RcpNumber
    Product.PLU = msg.PLU
    Product.TransactionStatusName = msg.TransactionStatusName
    Product.TransactionStatusCode = msg.TransactionStatusCode

    #jsObjOut = json.loads(msg)

    return purchase



