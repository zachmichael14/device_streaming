
from src.clients.usbamp_client import USBAmpClient
import pygds as g

# def main():
    ### USBAMP TEST ###
    # usb_amp = USBAmpClient()
    # if not usb_amp.connect():
    #     return
    # d = usb_amp.connection
    
    
    # scope = g.Scope(1/d.SamplingRate, title="Channels: %s", ylabel = u"U[μV]")
    # a = d.GetData(d.SamplingRate//2,scope)

    # del scope
    

    # # Cleanup
    # usb_amp.disconnect()

# if __name__ == '__main__':
    # print("main")
    # main()