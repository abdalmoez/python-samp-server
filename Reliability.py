
class Tools:
    def GetBit(data, offset, leftToRight=True):
        base = int(offset // 8)
        if(leftToRight):
            shift = int(7 - offset % 8)
        else:
            shift = int(offset % 8)
        return (data[base] & (1 << shift)) >> shift

    def GetUInt8(data, offset, leftToRight=True):
        base = int(offset // 8)
        if(leftToRight):
            shift = int(8 - offset % 8)
        else:
            shift = int(offset % 8)
        
        if(shift==0):
            return data[base]

        high_mask = (0xFF >> (8-shift))
        low_mask  = (0xFF << shift) & 0xFF
        # print(  ("shift",shift), 
        #         ("low_mask",low_mask),
        #         ("high_mask",high_mask) ,
        #         ("highvalue",((data[base] & high_mask)<< (8-shift))) , 
        #         ("lowvalue" ,((data[base+1] & low_mask) >> shift)))
        return ((data[base] & high_mask) << (8-shift)) + ((data[base+1] & low_mask)>>shift)
    def GetUInt16(data, offset, leftToRight=True):
        return Tools.GetUInt8(data,offset, leftToRight) + (Tools.GetUInt8(data,offset + 8, leftToRight) << 8)
    def GetUInt32(data, offset, leftToRight=True):
        return Tools.GetUInt16(data,offset, leftToRight) + (Tools.GetUInt16(data,offset + 16, leftToRight) << 16)
    def GetBits(data, offset, count, leftToRight=True):
        counter = 0
        value   = 0
        while(counter < count - count % 8):
            value += Tools.GetUInt8(data, offset + counter, leftToRight) << counter
            counter += 8
        while(counter < count):
            value += Tools.GetBit(data, offset + counter, leftToRight) << counter
            counter += 1
        return value
    @staticmethod
    def ReadCompressedUInt16(data, offset, unsignedData):
        size            = 16
        currentByte     = ( size >> 3 ) - 1
        byteMatch       = 0
        halfByteMatch   = 0
        output          = [0,0]
        if ( unsignedData == False ):
            byteMatch     = 0xFF
            halfByteMatch = 0xF0
        
        # Upper bytes are specified with a single 1 if they match byteMatch
        # From high byte to low byte, if high byte is a byteMatch then write a 1 bit. Otherwise write a 0 bit and then write the remaining bytes
        
        while ( currentByte > 0 ):
            # If we read a 1 then the data is byteMatch.
            b = Tools.GetBit(data, offset)
            if ( b != 0 ):   # Check that bit
                output[ currentByte ] = byteMatch
                currentByte -= 1
                offset += 1
            else:
                # Read the rest of the bytes
                output[0] = Tools.GetBits(data , offset, ( currentByte + 1 ) << 3)
                return (output[1] << 8) + output[0]
        # All but the first bytes are byteMatch.  If the upper half of the last byte is a 0 (positive) or 16 (negative) then what we read will be a 1 and the remaining 4 bits.
        # Otherwise we read a 0 and the 8 bytes
        b = Tools.GetBit(data, offset)
        offset += 1
        if ( b!= 0):  # Check that bit
            output[currentByte] = Tools.GetBits(data , offset, 4)
            offset += 4                
            output[ currentByte ] |= halfByteMatch; # We have to set the high 4 bits since these are set to 0 by ReadBits
        else:
            output[currentByte] = Tools.GetUInt8(data, offset)
            offset += 8
        return (output[1] << 8) + output[0]
    
    

class Reliability:
    def __init__(self, rawMsg):
        idx  = 0
        self.isResended =  Tools.GetBit(rawMsg, idx)
        idx += 1
        self.messageNumber = Tools.GetUInt16(rawMsg, idx)
        idx += 16
        self.reliability = Tools.GetBits(rawMsg, idx,4, False)
        idx += 4
        self.isPacketSplited =  Tools.GetBit(rawMsg, idx) != 0
        idx += 1
        self.dataLength = Tools.ReadCompressedUInt16(rawMsg, idx, True)
        idx += 6
        if(idx % 8 != 0):
            idx = (idx // 8) + 1
        else:
            idx = (idx // 8)
        self.data = rawMsg[idx:]
        if(len(self.data) != self.dataLength):
            raise IndexError
            print("[!] Unvalid length. Expected: ", self.dataLength, " Found: ", len(self.data), " currentIndex: ", idx)
    def processData(self):
        if(self.data[0] == ID_CONNECTION_REQUEST):
            print(ID_CONNECTION_REQUEST)
    def __str__(self):
        return ( "[isResended="+ str(self.isResended)+
                "|messageNumber="+ str(self.messageNumber)+
                "|reliability="+ str(self.reliability)+
                "|dataLength="+ str(self.dataLength)+
                "|data="+ str(self.data)+ "]")






        
# k = Reliability([0x00,0x00,0x43,0x80,0x0b])
#k = Reliability([0x00, 0x00, 0x43, 0x80, 0x0b])
#print(k.__str__())

