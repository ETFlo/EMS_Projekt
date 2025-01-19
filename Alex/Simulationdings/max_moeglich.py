from net_v2 import simulate


def optimieren(with_bat, epsilon):
    uebergabe_mid=10
    for zeit in [1,2,3]:
        print("Zeit: ", zeit)
        i=0
        lower_bound = 0
        upper_bound = 2
        while upper_bound - lower_bound > epsilon:
            mid = (upper_bound + lower_bound)/2
            if with_bat:
                anzahl = simulate(4.758e+01 , 2.847e+01 , 2.330e+01  ,7.205e+00,  5.220e-01,  1.704e-01,  5.831e+00 , 3.784e+00, mid, 0.541102409362793, False, zeit)  # Differential-Evolution Verfahren t -> 15000 - 15600 popsize = 5 
            else:
                anzahl = simulate(0, 0, 0, 0, 0, 0, 0, 0, mid, 0.541102409362793, False, zeit)
            if anzahl >0:
                upper_bound = mid
            else:
                lower_bound = mid
            #print(mid)
        
        if uebergabe_mid > mid:
            uebergabe_mid = mid
        print("Mid: ", mid)
        print("Uebergabe Mid: ",uebergabe_mid)
    if with_bat:
        anzahl = simulate(4.758e+01 , 2.847e+01 , 2.330e+01  ,7.205e+00,  5.220e-01,  1.704e-01,  5.831e+00 , 3.784e+00, mid, 0.541102409362793, True, zeit)  # Differential-Evolution Verfahren t -> 15000 - 15600 popsize = 5 
    else:
        anzahl = simulate(0, 0, 0, 0, 0, 0, 0, 0, mid, 0.541102409362793, True, zeit)
    return uebergabe_mid


epsilon = 0.000001

print("OPTIMIERUNG")
ohneBat = optimieren(False, epsilon)
print("Ohne Batterie: ", ohneBat)
mitBat = optimieren(True, epsilon)
print("Mit Batterie: ", mitBat)
print("Faktor: ", (mitBat/ohneBat-1)*100)