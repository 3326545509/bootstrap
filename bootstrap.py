import numpy as np 
from matplotlib import pyplot as plt
import json
import os 

def read_gamma_file(file):
    data    =   []
    with open(file,'r')as f:
        temp    =   f.readlines()
        for t in temp:
            if "#" in t:
                continue
            else:
                data.append(float(t.split()[-2]))
    return data

def bootstrap(num_bootstraps,data):

    each_resample_mean  =   []
    each_resample_std   =   []

    for i in range(num_bootstraps):
        resampled_data  =   np.random.choice(data,size=len(data),replace=True)

        each_resample_mean.append(np.mean(resampled_data))
        each_resample_std.append(np.std(resampled_data))

        draw_vertical(resampled_data,i+1)

    return each_resample_mean,each_resample_std

def draw_vertical(data,index):
    if index == 0:
        plt.errorbar(index,np.mean(data),yerr=np.std(data),color='red',ecolor='red',fmt='o',label='Origin data')
    elif index ==1:
        plt.errorbar(index,np.mean(data),yerr=np.std(data),color='black',ecolor='grey',fmt='o',label='Resampled data')
    else:
        plt.errorbar(index,np.mean(data),yerr=np.std(data),color='black',ecolor='grey',fmt='o')

def draw_bar(data,origin_result,houzui,out_dire_path):
    plt.hist(data,bins='auto',orientation='vertical',color='grey')
    plt.xlabel('Standard deviation of attenuation coef')
    plt.ylabel('Number')
    plt.axvline(x=np.mean(data),color='blue',label='Resampled data')
    plt.axvline(x=origin_result,color='red',label='Origin data',linestyle='--')
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig(out_dire_path+'/hist'+houzui+'.png')
    plt.close()

def strToPeriod(houzui):
    t1  =   float(houzui.split('to')[0])
    t2  =   float(houzui.split('to')[1])
    average_freq    =   (1/t1+1/t2)/2
    average_period  =   1/average_freq
    return average_period

def draw_final_mean_and_std(attenuation_coef,out_dire_path):
    x       =       attenuation_coef['Periods']
    y1      =       attenuation_coef['Origin']['Mean']
    error1  =       attenuation_coef['Origin']['Std']
    y2      =       attenuation_coef['Resampled']['Mean']
    error2  =       attenuation_coef['Resampled']['Std']

    plt.errorbar(x,y1,yerr=error1,elinewidth=1.5,capsize=4,color='blue',ecolor='blue',fmt='o',label='Origin',zorder=1,markersize=6,linewidth=2)
    plt.errorbar(x,y2,yerr=error2,elinewidth=1.5,capsize=4,color='red',ecolor='red',fmt='o',label='Bootstrap',zorder=1,markersize=6,linewidth=2)
    plt.legend(loc='best')
    plt.xlabel('Period (s)')
    plt.ylabel(r'Attenuation coef ($km^{-1}$)')
    plt.tight_layout()
    plt.savefig(out_dire_path+'/all.png')

def save_3list(list1,list2,list3,path):
    #list1~3: period mean std
    data    =   np.array([list1,list2,list3]).T
    np.savetxt(path+'/new_gamma.txt',data)
    
if __name__=='__main__':
    with open('parameter.json','r')as f:
        config  =   json.load(f)
        houzuis =   config['Houzuis']
        in_dire_path   =   config['In_dire_path']
        out_dire_path   =   config['Out_dire_path']

    os.system('mkdir '+out_dire_path)

    attenuation_coef={'Periods':[], 'Origin':{'Mean':[],'Std':[]}, 'Resampled':{'Mean':[],'Std':[]}}

    for houzui in houzuis:
        attenuation_coef['Periods'].append(strToPeriod(houzui))

        file    =   in_dire_path+'/'+houzui+'_gamma.txt'
        origin_data    =   read_gamma_file(file)
        attenuation_coef['Origin']['Mean'].append(np.mean(origin_data))
        attenuation_coef['Origin']['Std'].append(np.std(origin_data))

        each_resample_mean,each_resample_std   =   bootstrap(num_bootstraps=1000,data=origin_data)
        attenuation_coef['Resampled']['Mean'].append(np.mean(each_resample_mean))
        attenuation_coef['Resampled']['Std'].append(2*np.std(each_resample_mean)) #3 times std

        draw_vertical(origin_data,0)
        plt.xlabel('Number of resemple')
        plt.ylabel(r'Attenuation coef ($km^{-1}$)')
        plt.legend(loc='best')
        plt.tight_layout()
        plt.savefig(out_dire_path+'/resemple'+houzui+'.png')
        plt.close()

        draw_bar(each_resample_mean,np.mean(origin_data),houzui,out_dire_path)
        print(np.std(origin_data),np.mean(each_resample_std))
    
    draw_final_mean_and_std(attenuation_coef,out_dire_path)
    save_3list(attenuation_coef['Periods'],attenuation_coef['Resampled']['Mean'],attenuation_coef['Resampled']['Std'],out_dire_path)
