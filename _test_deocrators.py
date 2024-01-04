

def decor2(func):
    def Inner_Function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return func(*args , def_ret = True , **kwargs)
    return Inner_Function
    
@decor2
def test(url,*args , def_ret = False , **kwargs):
    if def_ret: return 'DEFAULT'
    if type(url) == str:
        return url
    else:
        raise Exception("")
    
print(test(1))
print(test('1','t'))
print(test('1','t', def_ret = True ))