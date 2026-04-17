import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
#from iminuit import Minuit
import random
#from scipy.stats import chi2
#from scipy.special import gammaln
#from scipy.stats import chisquare
import time
import os
import subprocess
import copy
import numpy as np
import yaml
from pathlib import Path
from importlib import import_module
import datetime
import scipy.stats
import math
import sys

E=4730.
me = 0.5109989461*10**6   #electron mass eV
g = E*1.0e6/me            #gamma factor
o = 2.3526413364          #eV Initial laser photon 527 nm
kappa = 4.*g*o/me
L = 30 * 10**3
lx = 20
ly = 32
#num_x = int(lx/size_x) #количество бинов вдоль оси x
#num_y = int(ly/size_y)


def make_central_coord(x,y):
    x_mid = (x[1:] + x[:-1])/2
    y_mid = (y[1:] + y[:-1])/2
    return [x_mid, y_mid]


def make_fit(config, h_dict, par):
    #data_left = h_dict['hc_l']
    #data_right = h_dict['hc_r']
    xy_coord = make_central_coord(h_dict['xc'], h_dict['yc'])
    cfg = copy.deepcopy(config)
    if  cfg['model_params']['E'][0] < 1000 : 
        cfg['model_params']['E'][0] = h_dict['env_params']['vepp4E']

    fit_method = cfg['fit_method'] #Importing module with desired fit method
    full_src_fname = os.getcwd()+'fit_method'+str(fit_method)
    fit_method_module = import_module('fit_method'+str(fit_method), full_src_fname)
    padding = cfg['padding']
    raw_data = (h_dict['hc_l'], h_dict['hc_r'])
    fm = eval('fit_method_module.FitMethod'+str(fit_method)+'(xy_coord, raw_data, padding=padding)')
    fm.fit(cfg, par)
    data_fields = fm.get_fit_result(cfg)

    return fm, data_fields

'''
def read_data(filename):
    h_dict = dict(np.load(filename, allow_pickle=True))
    return h_dict
    print(h_dict)
'''

def load_yaml(path: str) -> dict:
    file = Path(path)
    if not file.exists():
        print(f'ОШИБКА: Не могу открыть конфигурационный файл "{str}", оставляю параметры по умолчанию')
        return {}
    with file.open() as f:
        return yaml.safe_load(f) or {}


def init_figure(label):
    fig = plt.figure(figsize=(16, 8))
    fig.canvas.manager.set_window_title(label)

    # ---------- MAIN GRID ----------
    gs_main = gridspec.GridSpec(
        1, 4,
        figure=fig,
        width_ratios=[2, 2, 2, 1],
        hspace=0.1,
        wspace=0.4
    )

    gs_sum = gridspec.GridSpecFromSubplotSpec(
        2, 1,
        subplot_spec=gs_main[0],
        height_ratios=[1.0, 1.0],
        #width_ratios=[1.0, 1.0],
        hspace=0.1,
        wspace=0.05
    )

    gs2d_sum = gridspec.GridSpecFromSubplotSpec(
        2, 1,
        subplot_spec=gs_sum[0],
        height_ratios=[1.0, 1.0],
        #width_ratios=[1.0, 1.0],
        hspace=0.1,
        wspace=0.00
    )
    ax_sum_2d     = fig.add_subplot(gs2d_sum[0])
    #ax_sum_2d.set_ylabel(f"data")
    ax_sum_2d.get_xaxis().set_visible(False)

    ax_sum_fit    = fig.add_subplot(gs2d_sum[1],  sharex=ax_sum_2d)
    ax_sum_px     = fig.add_subplot(gs_sum[1], sharex=ax_sum_2d)

    gs_diff = gridspec.GridSpecFromSubplotSpec(
        2, 1,
        subplot_spec=gs_main[1],
        height_ratios=[1.0, 1.0],
        #width_ratios=[1.0, 1.0],
        hspace=0.1,
        wspace=0.05
    )

    gs2d_diff = gridspec.GridSpecFromSubplotSpec(
        2, 1,
        subplot_spec=gs_diff[0],
        height_ratios=[1.0, 1.0],
        #width_ratios=[1.0, 1.0],
        hspace=0.1,
        wspace=0.00
    )
    ax_diff_2d     = fig.add_subplot(gs2d_diff[0])
    ax_diff_2d.get_xaxis().set_visible(False)
    ax_diff_fit    = fig.add_subplot(gs2d_diff[1],  sharex=ax_diff_2d)
    ax_diff_px     = fig.add_subplot(gs_diff[1], sharex=ax_diff_2d)

    def add_title(ax, title : str):
        fig.text(
            x=ax.get_position().x0 + ax.get_position().width/2, 
            y=ax.get_position().y1 + 0.01, 
            s=title, 
            ha='center', va='bottom', fontsize=14
        )



    gs_center = gridspec.GridSpecFromSubplotSpec(
        2, 1,
        subplot_spec=gs_main[2],
        height_ratios=[1.0, 1.0],
        #width_ratios=[1.0, 1.0],
        hspace=0.1,
        wspace=0.1
    )

    ax_sum_py     = fig.add_subplot(gs_center[0], sharey=ax_sum_2d)
    ax_diff_py    = fig.add_subplot(gs_center[1], sharey=ax_diff_2d)


    ax_fitres_text = fig.add_subplot(gs_main[3])
    ax_fitres_text.axis('off')

    add_title(ax_sum_py, "vertical projection")
    add_title(ax_sum_2d, "$N^L + N^R$")
    add_title(ax_diff_2d, "$N^L - N^R$")
    add_title(ax_fitres_text, "Fit result")

    A = {
        'data_sum':  ax_sum_2d,
        'fit_sum':   ax_sum_fit,
        'sum_px':    ax_sum_px,
        'sum_py':    ax_sum_py,

        'data_diff': ax_diff_2d,
        'fit_diff':  ax_diff_fit,
        'diff_px':   ax_diff_px,
        'diff_py':   ax_diff_py,

        'fit_result': ax_fitres_text
    }
    return fig, A


def show_fit_results(ax, fitter, begintime, endtime):
    ax.axis('off')
    minuit = fitter.minuit
    result_text  = f'Method: {fitter.fit_method}'
    result_text += f'\n{"begin:":<7} {begintime}'
    result_text += f'\n{"end:":<7} {endtime}'
    #result_text += f'\n${"\\chi^2/n_{df}":<10} = {fitter.chi2:.{0 if fitter.chi2>10 else 2:}f}/{fitter.ndf} = {fitter.chi2/fitter.ndf:.{1 if fitter.chi2/fitter.ndf>10 else 2}f}$'
    
    label = r"\chi^2/n_{df}"
    c2 = fitter.chi2
    ndf = fitter.ndf
    val = c2 / ndf
    result_text += f'\n${label:<10} = {c2:.{0 if c2 > 10 else 2}f}/{ndf} = {val:.{1 if val > 10 else 2}f}$'
    prob = (1.0-scipy.stats.chi2.cdf(fitter.chi2, fitter.ndf))

    label_chi2 = r"\chi^2"
    result_text += f'\n${"prob({label_chi2})":<10} = {prob*100.0:.4g}\\%$'

    def smart_param_format(parname : str, title : str = "", format : str = "", unit : str="", scale=1.0):
        val = minuit.values[parname]
        err = minuit.errors[parname]
        name = parname if title == "" else title
        text = f'\n${name:<10} = {val*scale:{format}}$'
        if not minuit.fixed[parname]:
            text += f'$\\, \\pm \\, {err*scale:{format}}$'
        text += f" {unit}"
        return text

    for parname in fitter.parlist:
        try:
            if parname=='k' or parname=='L':
                if parname=='k':
                        result_text += smart_param_format("k", title = "k_{reg}", format=".2g")
                if parname=='L':
                        result_text += smart_param_format("L", format=".2f", scale=1e-3, unit="m")
            else:
                if not minuit.fixed[parname]:
                    if  parname == 'beta':
                        result_text += smart_param_format("beta", title="\\beta", format=".1f", unit="$^\\circ$", scale=180./math.pi)
                    elif  parname == 'DN':
                        result_text += smart_param_format("DN", title="\\delta N", format=".3g", unit="%", scale=100)
                    else:
                        result_text += smart_param_format(parname,  format=".3f")
        except KeyError: 
            print("Что-то не так в показе результатов подгонки")
            pass

    ax.text(0.5, 0.98, result_text, 
                transform=ax.transAxes, # Используем координаты осей (0-1)
                fontsize=14,                    # Подберите размер шрифта
                verticalalignment='top',       # Привязка к верхнему краю
                horizontalalignment='center',   # Привязка к правому краю
           #     bbox={'facecolor': 'white', 'alpha': 0.7, 'pad': 5} # Добавление фона для читаемости
        )
    return ax
def show_res(fitter, config, data_fields, Ax, begintime, endtime, num, path):
    #Очистим от предыдущих графиков
    for name, ax in Ax.items():
        ax.cla()

    total_figure_list = list(data_fields.keys())

    main_figure_list = []

    #print_fit_results(ax[0], fitter, begintime,endtime)
    show_fit_results(Ax['fit_result'], fitter, begintime,endtime)

    for kind in ['sum','diff']:
        for proj in [ 'px', 'py']:
            name=kind+"_"+proj
            data_fields['data_'+name].draw(Ax[name])
            main_figure_list.append('data_'+name)
            data_fields['fit_'+name].draw(Ax[name])
            main_figure_list.append('fit_'+name)
            Ax[name].grid()

    for kind in ['sum','diff']:
        for  model in ['data', 'fit']:
            name = model+"_"+kind
            data_fields[name].draw_2d_plot2(Ax[name])
            main_figure_list.append(name)

    remaining_figure_list = list(set(total_figure_list).difference(set(main_figure_list)))
    plt.show(block=False)
    #plt.show()
    plt.savefig(os.path.join(path, config['png_file_name'].replace('.png', f'_{num}.png')))
    plt.pause(1)
    return remaining_figure_list
'''
'''
def unx2str(unixtime):
    return datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d %H:%M:%S')

def draw(ax, config, fitter, data_fields, num, path): #рисуем результат подгонки
    remaining_figure_list = show_res(fitter, config,  data_fields, ax, unx2str(time.time()),unx2str(time.time()), num, path)

    #if self.config['draw_additional_figures'] and len(remaining_figure_list)>0:
    #    if not self.INIT_ADD_FIGURES:
    #        self.INIT_ADD_FIGURES = True
    #        self.fig1, self.ax1 = init_figure_gen('Laser Polarimeter additional plots', data_fields)
    #    show_res_gen(data_fields, self.ax1, remaining_figure_list, file_buffer[0])

def get_depol_state(times):
    return_state = []
    return_state.append( 
                        {
                            "timestamp"            : 0,
                            "revolution_frequency" : 0,
                            "harmonic_number"      : 0,
                            "attenuation"          : 0,
                            "frequency"            : 0,
                            "frequency_speed"      : 0,
                            "energy"               : 0,
                            "energy_speed"         : 0 
                            }
                        )
    try:
        #print("updating lsrp::depolarizer  PVs")
        epics.caput('lsrp:depolarizer:frequency', return_state[-1].frequency)
        epics.caput('lsrp:depolarizer:attenuation', return_state[-1].attenuation)
    except: 
        pass
    return return_state

def get_coor_grid():
    return {'xs': np.linspace(-64,64,num=33),
            'ys': np.linspace(-20,20, num=21),
            'xc': np.linspace(-32,32,num=33),
            'yc': np.linspace(-10,10, num=21)}

def make_hist_dict(hist_c_l, hist_c_r):
    hist_s_l = np.zeros((20,32))
    hist_s_r = np.zeros((20,32))
    #hist_c_l = np.zeros((20,32))
    #hist_c_r = np.zeros((20,32))

    

    grid = get_coor_grid()

    h_dict = { 'hc_l': hist_c_l,
                'hc_r' : hist_c_r,
                'hs_l' : hist_s_l,
                'hs_r' : hist_s_r,
                'xs' : grid['xs'],
                'ys' : grid['ys'],
                'xc' : grid['xc'],
                'yc' : grid['yc']}
    return h_dict
'''
def save_mapped_hist(params, filename, h_dict, env_params):
    np.savez(os.path.splitext(filename)[0]+'_' + 'P[' +  str(params[0]) + ']' + '_' + 'Q[' +  str(params[1]) + ']' + '_' + 'beta[' +  str(params[2]) + ']',
            hc_l = h_dict['hc_l'],
            hc_r = h_dict['hc_r'],
            #hs_l = h_dict['hs_l'],
            #hs_r = h_dict['hs_r'],
            #xs = h_dict['xs'],
            #ys = h_dict['ys'],
            xc = h_dict['xc'],
            yc = h_dict['yc'],
            env_params=env_params)
'''	
def create_dir(dir_path):
    path = "../fitting"
    dir_name = path + dir_path.replace("../output", "")
    os.mkdir(dir_name)
    return dir_name
    


def select_dir(base_path = ".."):
    available_dirs = [d for d in os.listdir(base_path) if d.startswith("output_") and os.path.isdir(os.path.join(base_path,d))]
    if not available_dirs:
        print("Нет доступных директорий")
        return None
    print("\nСписок доступных директорий: ")
    for i, dir_name in enumerate(available_dirs):
        disp = dir_name.replace("output_", "").split("_")
        if len(disp)>=2:
            print(f" {i}:{dir_name} (d_theta_x = {disp[0]}, d_theta_y = {disp[1]})")
        else:
            print(f" {i}:{dir_name}")
    try:
        choice = input("\n Выберите номер директории: ")

        index = int(choice)
        if 0<=index<=len(available_dirs):
            return os.path.join(base_path, available_dirs[index])
        else:
            print("Неверный номер")
            return None
    except:
        print("ERROR")
        return None


P = 0.0
beta = np.pi/4 + 0.03 


Q = 1.
'''
Q_min = 0.5
Q_max = 1
Q_steps = 11
'''


exe = '../build/./main'
macro = '../run.mac'
num = 0
#for q in np.linspace(Q_min, Q_max, Q_steps):
 
 
 
params = [P, Q, beta]


#cmd = subprocess.run([exe, macro, '--P', str(P), '--Q', str(Q), '--beta', str(beta)])

bins = [20,32] # число бинов
'''
sx = input("разброс по x: ")
sy = input("разброс по y: ")

out_dir = '../output_' + sx + '_' + sy'''

#out_dir = select_dir()

#проверяем аргументы
if len(sys.argv) < 2:
    print ("не указана дирректория для подгонки! \n")
    sys.exit(1)

out_dir = sys.argv[1]




#Гистограмма для правой поляризации
hist_r = np.loadtxt(out_dir + '/histogram_r_0.txt')
print(hist_r.shape)
#Гистограмма для левой поляризации
hist_l = np.loadtxt(out_dir + '/histogram_l_0.txt')

for i in range(0, 10):
    hist_r += np.loadtxt(out_dir + '/histogram_r_' + str(i) + '.txt')
    hist_l += np.loadtxt(out_dir + '/histogram_l_' + str(i) + '.txt')

'''	
np.savetxt('histogram_L.txt',hist_l, fmt='%d', delimiter=' ')
np.savetxt('histogram_R.txt',hist_r, fmt='%d', delimiter=' ')
'''
#заполнение словаря
begintime = time.time()

h_dict = make_hist_dict(hist_l, hist_r)

endtime = time.time()
#vepp4E - энергия ускорителя - 4730 + 30 МэВ
#vepp4H_nmr - 4730 МэВ / 1.042 (МэВ/Гс) - магнитное поле на орбите в гауссах - ведущее поле

vepp4E = 4760

vepp4H_nmr = 4730/1.042

real_E = 4730

env_params = {'vepp4E':vepp4E, 'vepp4H_nmr':vepp4H_nmr, 'real_E':real_E}

env_params['begintime'] = begintime

env_params['endtime'] = endtime

env_params['depolarizer'] = get_depol_state([begintime, endtime])

config = load_yaml("spotfit.yml")

print(config)

h_dict['env_params'] = {'vepp4E': 4730.0 }

print(h_dict)

par = out_dir.replace("../output_", "").split("_")

fitter, data_fields = make_fit(config, h_dict, par)

fig, ax = init_figure('Laser Polarimeter 2D Fit')

path = create_dir(out_dir)
draw(ax, config, fitter, data_fields, num, path)

plt.show(block=True)
plt.close()
#save_mapped_hist(params, 'histogram.npz', h_dict, env_params)
#       num += 1

bins_x = np.arange(0, 20, 1)
bins_y = np.arange(0,64,2)

plt.imshow(hist_l - hist_r, aspect = 'auto', extent = [0, np.max(bins_x), 0, np.max(bins_y)], cmap = 'viridis', origin = 'lower')

plt.colorbar()

plt.savefig(os.path.join(path, 'difference.png'), dpi = 150, bbox_inches='tight')
plt.close()
#plt.show()
