from color import Colors as C

class Exceptions():
    def __init__(self) -> None:
        pass

    def typeChecker(origin:str,param:list, check:list,strict=False):
        print(C.ok("checking"+str(param)))
        print(C.ok("cmmp"+str(check)))


        if (len(param)!=len(check)):
            print(C.error("["+origin+"] ERROR:"+(str(len(check)))+" arguments were expected but "+(str(len(param)))+" were given"))
            raise BaseException()
        

        for i in range (len(param)):


            if (((type(check[i]))==list)):
                if ((type(param[i]))==list):
                    obj = Exceptions()
                    obj.typeCheckerRek(origin,param[i],check[i],strict)
                else:
                    print(C.error("["+origin+"] ERROR: Type "+(str(type(check[i])))+" was expected as "+(str(i))+"-th argument but "+(str(type(param[i])))+" was found"))
                    raise BaseException()

            elif ((type((param[i]))!=check[i]) and not (issubclass(type(param[i]),check[i])) and not strict ):
                print(C.error("["+origin+"] ERROR: Type "+(str(check[i]))+" was expected as "+(str(i))+"-th argument but "+(str(type(param[i])))+" was found"))
                raise BaseException()
            
            elif ((type((param[i]))!=check[i]) and strict ):
                print(C.error("["+origin+"] ERROR: Type "+(str(check[i]))+" was expected as "+(str(i))+"-th argument but "+(str(type(param[i])))+" was found"))
                raise BaseException()
            
        print(C.checkSuc("["+origin+"] SUCCESS: Type check completed successfully"))

        return
    
    def typeCheckerRek(self,origin:str,param:list, check:list, strict:bool):
        #print(C.ok("checking"+str(param)))
        #print(C.ok("cmmp"+str(check)))
        
        if (len(param)!=len(check)):
            print(C.error("["+origin+"] ERROR:"+(str(len(check)))+" arguments were expected but "+(str(len(param)))+" were given"))
            raise BaseException()
        

        for i in range (len(param)):

            if (((type(check[i]))==list)):
                if ((type(param[i]))==list):
                    self.typeCheckerRek(origin,param[i],check[i])
                else:
                    print(C.error("["+origin+"] ERROR: Type "+(str(type(check[i])))+" was expected as "+(str(i))+"-th argument but "+(str(type(param[i])))+" was found"))
                    raise BaseException()
            elif ((type((param[i]))!=check[i]) and not (issubclass(type(param[i]),check[i])) and not strict ):
                print(C.error("["+origin+"] ERROR: Type "+(str(check[i]))+" was expected as "+(str(i))+"-th argument but "+(str(type(param[i])))+" was found"))
                raise BaseException()
            elif ((type((param[i]))!=check[i]) and strict ):
                print(C.error("["+origin+"] ERROR: Type "+(str(check[i]))+" was expected as "+(str(i))+"-th argument but "+(str(type(param[i])))+" was found"))
                raise BaseException()
        return
    
    
            
    def boundChecker(origin:str,varname:str,val:float, lower:float,upper:float):
        if ((val > upper) or (val < lower)):
            print(C.warning("["+origin+"] WARNING: The variable "+varname+" was expected to be in the range ["+str(lower)+","+str(upper)+"] but was "+str(val)))
        else:
            print(C.checkSuc("["+origin+"] SUCCESS: Range check of "+varname+" completed successfully"))

                    
