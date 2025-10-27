import json
class Purchase:
  def __init__(self, data):
    self.UUID = data["Purchase"]["UUID"]
    self.TimeOutInMs = data["Purchase"]["TimeOutInMs"]
    self.Date = data["Purchase"]["Date"]
    self.Time = data["Purchase"]["Time"]
    self.UnixEpochTimeInMs = data["Purchase"]["UnixEpochTimeInMs"]
    self.MachineID = data["Purchase"]["MachineID"]
    self.MessageType = data["Purchase"]["MessageType"]
    self.MessageTypeName = data["Purchase"]["MessageTypeName"]
    self.ErrorNumbers = data["Purchase"]["ErrorNumbers"]

    order_data = data["Purchase"]["Order"]
    self.Order = Order(order_data)

  def toJson(self):
    return {
        "Purchase": {
            "UUID": self.UUID,
            "TimeOutInMs": self.TimeOutInMs,
            "Date": self.Date,
            "Time": self.Time,
            "UnixEpochTimeInMs": self.UnixEpochTimeInMs,
            "MachineID": self.MachineID,
            "MessageType": self.MessageType,
            "MessageTypeName": self.MessageTypeName,
            "ErrorNumbers": self.ErrorNumbers,
            "Order": self.Order.toJson()
        }
    }

class Order:
  def __init__(self, data):
    self.BarcodeKey = data["BarcodeKey"]
    self.Products = [Product(product_data) for product_data in data["Product"]]

  def toJson(self):
    return {
        "BarcodeKey": self.BarcodeKey,
        "Product": [Product.toJson() for Product in self.Products]
    }

class Product:
  def __init__(self, data):
    self.PLU = data["PLU"]
    self.RcpNumber = data["RcpNumber"]
    self.RcpName = data["RcpName"]
    self.Price = data["Price"]
    self.Currency = data["Currency"]
    self.SML = data["SML"]
    self.Quantity = data["Quantity"]
    self.Notification = data["Notification"]
    self.TransactionStatusCode = data["TransactionStatusCode"]
    self.TransactionStatusName = data["TransactionStatusName"]

  def toJson(self):
    return {
        "PLU": self.PLU,
        "RcpNumber": self.RcpNumber,
        "RcpName": self.RcpName,
        "Price": self.Price,
        "Currency": self.Currency,
        "SML": self.SML,
        "Quantity": self.Quantity,
        "Notification": self.Notification,
        "TransactionStatusCode": self.TransactionStatusCode,
        "TransactionStatusName": self.TransactionStatusName
    }