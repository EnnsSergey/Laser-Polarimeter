import numpy as np
from iminuit import Minuit
from iminuit.util import make_func_code
from scipy import signal
from math import cos,sin
import matplotlib.pyplot as plt

import sys

def get_coor_grid():
    return {'xs': np.linspace(-64,64,num=33),
            'ys': np.linspace(-20,20, num=21),
            'xc': np.linspace(-32, 32,num=33),
            'yc': np.linspace(-10,10, num=21)}

class data_field:
    def __init__(self, coors, data, data_err = None, label=None, data_type='dat'):
        self.x = coors[0]
        self.y = coors[1]
        self.data = data
        self.data_err = data_err
        self.label = label
        self.data_type = data_type
        self.interpolation = 'none'
        self.palette = plt.cm.viridis

    def draw_profilex(self, ax):
        x = (self.x[1:]+self.x[:-1])/2
        y = self.data
        ax.bar(x, y,
                  yerr=self.data_err,
                  color='white',#color='lightseagreen',
                  edgecolor='white',
                  linewidth=1,
                  width=2,
                  zorder=1)
        if self.data_type == 'dat':
            ax.plot(x, y, marker="o", markersize=5, linestyle="", alpha=0.8, color="blue",zorder=3, label = self.label)
        else:
            ax.plot(x, y, color = 'red', zorder=4, label = self.label)
        ax.grid(zorder=0)
        ax.set_xlabel(r'x [mm]')
        #ax.legend()

#    def draw_profile(self, ax):
#        x = (self.y[1:]+self.y[:-1])/2
#        y = self.data 
#        ax.bar(x, 
#                   y,
#                   yerr=self.data_err,
#                   color='white',
#                   edgecolor='white',
#                   linewidth=1,
#               #height=1,
#                   zorder=1)
#        if self.data_type == 'dat':
#            ax.plot(x, y, marker="o", markersize=5, linestyle="", alpha=0.8, color="blue",zorder=3, label = self.label)
#        else:
#            ax.plot(x,y, color = 'red', zorder=4, label = self.label)
#        ax.grid(zorder=0)
#        ax.set_xlabel(r'y [mm]')
#        #ax.legend()
    
    def draw_profiley(self, ax):
        y = (self.y[1:]+self.y[:-1])/2
        x = self.data #We need to change x <-> y because of using barh
        ax.barh(y, 
                   x,
                   xerr=self.data_err,
                   color='white',
                   edgecolor='white',
                   linewidth=1,
                   height=1,
                   zorder=1)
        if self.data_type == 'dat':
            ax.plot(x, y, marker="o", markersize=5, linestyle="", alpha=0.8, color="blue",zorder=3, label = self.label)
        else:
            ax.plot(x,y, color = 'red', zorder=4, label = self.label)
        ax.grid(zorder=0)
        ax.set_ylabel(r'y [mm]')
        #ax.legend()

    def draw_2d_plot2(self, ax):
        im_dat = ax.imshow( self.data, 
                            cmap=self.palette,
                            interpolation=self.interpolation,
                            extent=[self.x[0],self.x[-1],self.y[0],self.y[-1]],
                            origin='lower')
        #cbar_dat = fig.colorbar(im_dat, ax=ax)
        #ax.grid()
        ax.set_aspect('auto')
        #ax.set_title(self.label)
        #ax.set_xlabel(r'x [mm]')
        #ax.set_ylabel(r'y [mm]')
        
    def draw_2d_plot(self, ax):
        im_dat = ax.imshow( self.data, 
                            cmap=self.palette,
                            interpolation=self.interpolation,
                            extent=[self.x[0],self.x[-1],self.y[0],self.y[-1]],
                            origin='lower')
        #cbar_dat = fig.colorbar(im_dat, ax=ax)
        #ax.grid()
        ax.set_aspect('equal')
        ax.set_title(self.label)
        ax.set_xlabel(r'x [mm]')
        ax.set_ylabel(r'y [mm]')
        #ax.get_xaxis().set_visible(False)

    def draw(self, ax):
        if self.y is None:
            self.draw_profilex(ax)
        elif self.x is None: 
            self.draw_profiley(ax)
        else:
            self.draw_2d_plot(ax)





#Fit by Fourier reconstruction of beam shape * Compton to normalized data difference
class FitMethod3:

    def __init__(self, x, data, padding = (22,16), reg_eps = 1e-12 ):
        self.fit_method=3
        self.x = x
        #ненормированные (сырые) данные
        self.raw_data_left, self.raw_data_right = data

        if self.raw_data_left.shape != self.raw_data_right.shape:
            raise ValueError(f"Размеры массивов не совпадают: "
                            f"raw_data_left.shape={self.raw_data_left.shape}, "
                            f"raw_data_right.shape={self.raw_data_right.shape}")

        self.shape = np.shape(self.raw_data_left)
        self.padding = padding
        self.ext_shape = (self.shape[0] + 2*self.padding[0], self.shape[1] + 2*self.padding[1])
        print("Padding = ", self.padding, "Extended shape = ", self.ext_shape)
        self.xx, self.yy = self.extend_grid2(self.x[0], self.x[1], self.padding)
        self.reg_eps = reg_eps


        fit_varnames  = list(self.ComptonPDF.__code__.co_varnames)[3:self.ComptonPDF.__code__.co_argcount]+['DN','k']
        self.parlist = fit_varnames
        self.inipars = dict.fromkeys(fit_varnames, 1.0)
        self._parameters = {name: None for name in fit_varnames}
        self.minuit = Minuit(self, **self.inipars)
        self.minuit.print_level = 0
        self.minuit.errordef=1
        self.efficiency = np.ones(self.shape)

        def set_par(name, value, error, limits, fix):
            self.minuit.values[name] = value
            self.minuit.errors[name] = error
            self.minuit.limits[name] = limits
            self.minuit.fixed[name] = fix

        set_par('E'    , 4730  , 0.1 , [4000 , 5000] , True)
        set_par('L'    , 28e3  , 0.1 , [20e3 , 35e3] , True)
        set_par('P'    , 0.0   , 0.1 , [-1.0 , 1.0]  , False)
        set_par('V'    , 0.0   , 0.1 , [-1.0 , 1.0]  , True)
        set_par('Q'    , 0.0   , 0.1 , [-1.0 , 1.0]  , False)
        set_par('beta' , 0.0   , 0.1 , [-7.0 , +7.0] , False)
        set_par('alpha', 0.0   , 0.1 , [-7.0 , +7.0] , True)
        set_par('DN'   , 1     , 0.1 , [0.   , 1e10] , False)
        set_par('k'    , 6e-4  , 0.1 , [0.   , 1.]   , True)

    def ComptonPDF(self, x,y, E, L, P , V , Q, beta, alpha):
        me = 0.5109989461*10**6   #electorn mass eV
        gamma = E*1.0e6/me            #gamma factor
        omega = 2.3526413364          #eV Initial laser photon 527 nm
        
        r = np.hypot(x,y)
        phi = np.arctan2(y, x)

        eta = gamma*r/L
        eta2 = np.power(eta,2.0)
        
        kappa = 4.0*gamma*omega/me

        t = 1. + eta2 + kappa

        A = np.power(1.0+kappa,2.0)/(1.0 + 0.5*kappa**2/(1+kappa))
        
        sigma = A/np.power(t,2.)*( 1. + 0.5*(kappa**2.)/(t*(1.+eta2)) -
                + 2.* (eta/(1.+eta2))**2  * (1.0 - Q * np.cos(2.*(phi-beta)))+
                + P*V*eta*kappa / (t * ( 1. + eta2 ) ) * np.sin(phi-alpha)
            )
        return sigma


    #def Gaus(self, x, y, mx, my, sx, sy):
    #    return  np.exp(  - 0.5*(np.power( (x-mx)/sx, 2.0) + np.power( (y-my)/sy , 2.0) ) )/(2.0*np.pi*sx*sy)


    def extend(self, data, padding):
        new  = np.zeros( ( data.shape[0]+padding[0]*2, data.shape[1]+padding[1]*2 ) )
        new[ padding[0]:-padding[0], padding[1]: -padding[1] ] = data
        return new

    def extend_from_base(self, data, base):
        new  = base.copy()
        padding = ( (base.shape[0]-data.shape[0])//2, (base.shape[1]-data.shape[1])//2 )
        new[ padding[0]:-padding[0], padding[1]: -padding[1] ] = data
        return new

    def arrange(self, data, base):
        padding = ( (base.shape[0]-data.shape[0])//2, (base.shape[1]-data.shape[1])//2 )
        #data[0:padding[0], 0: ]  = base[0:padding[0], 0: ]
        #data[-padding[0]:-1, 0: ]  = data[-padding[0]:-1, 0: ]
        new = base.copy()
        new[ padding[0]:-padding[0], padding[1]: -padding[1] ]  = data[ padding[0]:-padding[0], padding[1]: -padding[1] ]

    def shrink(self,data):
        py, px = self.padding
        ly, lx = self.shape
        return data[py : py + ly, px : px + lx]


    #calculate Fourier image of beam pdf (regularized)
    def fBeamPDF(self, data, compton, add_shape, k=6e-4, eps=1e-9):
        fC  = np.fft.fft2(model) #Fourier image of model
        fD  = np.fft.fft2(data)  #Fourier image of data
        A2 = np.sum(np.abs(fC*fC)) #normalization constant
        R = np.abs(fC*fC) / ( np.abs(fC*fC) + k*A2) #regularization koeff
        fB = fD0/( fC0 + eps)*R
        return fB

    def calc_chi2(self, data, fit, error):
        return np.sum( np.where(error > 0,  np.abs( np.power( (data-fit)/error,2.0)),  0.0) ) 

    def extend_grid1(self, x, n):
        #    ...+9....#########...+9.... extend region +9+9
        step = x[1]-x[0]
        x_left  = np.linspace(x[0]-n*step,x[0], num=n, endpoint=False)
        x_right = np.linspace(x[-1]+step, x[-1]+(n+1)*step, num=n, endpoint=False)
        return np.concatenate((x_left, x, x_right))

    def extend_grid2(self, x, y, padding):
        ey = self.extend_grid1(y,padding[0])
        ex = self.extend_grid1(x,padding[1])
        #print('ey=', ey, ' shape =', ey.shape)
        #print('ex=', ex, ' shape = ', ex.shape)
        return  np.meshgrid(ex,ey)

    def print_his(self, data, width=6):
        print(''.rjust(width*data.shape[1],'━'))
        for y in range(0, data.shape[0]):
            for x in range(0, data.shape[1]):
                print( '{:+{}.1f}'.format(data[y,x], width), end='')
            print('')
        print(''.rjust(width*data.shape[1],'━'))

    def shift_phase2(self, data, phases):
        shape = np.shape(data)
        idx =  np.indices(shape)
        z = np.exp ( - 1.0j*np.pi*( idx[0]*phases[0] +  idx[1]*phases[1] ) )
        return data*z

    def smooth(self, his, window=3): 
        smooth_kernel = np.blackman(window)
        smooth_kernel = [x*smooth_kernel  for x in smooth_kernel]
        return  signal.fftconvolve(his, smooth_kernel, 'same')

    def fft_fix(self, D):
        n2y=D.shape[0]//2
        n2x=D.shape[1]//2
        D = np.vstack([D[n2y:,],D[0:n2y,]])
        D = np.hstack([D[:,n2x:],D[:,0:n2x]])
        return D

    def __call__(self, *par):  
        #Надо внимательно соблюдать порядок переменных 
        #чтобы в точности совпадало с порядком параметров minuit
        E, L, P,  V, Q,  beta, alpha, DN, k = par
        NL = self.N*(1.0 + 0.5*DN)
        NR = self.N*(1.0 - 0.5*DN)
        if self.tied_VQ:
            V = np.sqrt(1.-Q*Q)

        #Вычисляем комптоновское сечение
        self.compton_left  = self.ComptonPDF(self.xx, self.yy, E, L, P,  V,  Q, beta, alpha)
        self.compton_right = self.ComptonPDF(self.xx, self.yy, E, L, P, -V, -Q, beta, alpha)

        self.compton_sum  = self.compton_left + self.compton_right
        self.compton_diff = self.compton_left - self.compton_right


        #Нормируем данные на число событий. Данное действие зависит от параметра подгонки DN
        self.data_left  = self.raw_data_left/NL
        self.data_right = self.raw_data_right/NR
        self.data_left_error =  np.sqrt(self.raw_data_left)/NL
        self.data_right_error = np.sqrt(self.raw_data_right)/NR

        #sum and difference for data
        self.data_sum  = self.data_left + self.data_right
        self.data_diff = self.data_left - self.data_right
        self.data_sum_error = np.sqrt(self.data_left/NL + self.data_right/NR)



        #делаем фурье преобразования на расширенной области
        fC0  = np.fft.fft2(self.compton_sum)
        fC1  = np.fft.fft2(self.compton_diff)
        fD0  = np.fft.fft2(self.extend_from_base(self.data_sum, self.cb0) )

        #временная переменная
        fC02  = np.abs(fC0)**2
        #Теперь вычисляем фурье образ функции пучка используя регуляризацию Винера
        fB = fD0 * np.conj(fC0) / (fC02  + k * np.sum(fC02)  + 1e-15)
        #print("fC02 stat ", "sum = ", np.sum(fC02), "max = " , np.max(fC02), " sum / size = ", np.sum(fC02)/fC02.size, "size = ", fC02.size, "sum /max = ", np.sum(fC02)/np.max(fC02))


        fB = self.shift_phase2(fB,[1.0,1.0])

        #Подставляем полученный фурье образ пучка в свёртку и вычисляем её через обратное преобразование фурье
        CB0 = np.real(np.fft.ifft2(fC0*fB))
        CB1 = np.real(np.fft.ifft2(fC1*fB))
        #Запомим расширенную свёртку в расширенной области, чтобы итеративно использовать 
        #кажется это медленная операция. Но как быть?
        self.CB0 = CB0.copy()
        self.CB1 = CB1.copy()

        B =  np.real(np.fft.ifft2(fB))


        D0   = self.data_sum
        D1   = self.data_diff
        CB1  = self.shrink(CB1)
        CB0  = self.shrink(CB0)
        B    = self.shrink(B)

        ##симметричная по функции B модель
        self.fit_diff        =  D0*CB1
        self.data_diff       =  D1*CB0
        self.data_diff_error = np.sqrt( np.power( CB0 - CB1, 2.0) * self.data_left/NL + np.power( CB0 + CB1, 2.0) * self.data_right/NR)

        chi2_diff  = self.calc_chi2( self.data_diff ,  self.fit_diff, self.data_diff_error)   


        #Подготовка к вычислению хи квадрат для неполяризованной части
        self.fit_sum  = CB0
        #self.data_sum = D0
        #self.data_sum_error = self.data_sum_error

        chi2_L = ((L-self.L)/self.Lerror)**2

        chi2 = chi2_diff  + chi2_L

        if np.isnan(chi2): chi2_sum = 1e100

        self.beam_shape = B
        
        x = D0/CB0
        average = np.sum(x)/(x.shape[0]*x.shape[1])
        self.efficiency = np.where( np.abs(self.raw_data_left + self.raw_data_right)<1.0 , average, x)

        #self.remains  = (self.fit_diff - self.data_diff)/self.data_diff_error
        self.remains  = (self.fit_diff - self.data_diff)
        if np.isnan(chi2): return 1e100
        return chi2

    def perimeter_norm(self, data):
        shape = data.shape
        s = np.sum( data[0:,0:0] )
        s+= np.sum( data[0:, -1:-1] )
        s+= np.sum( data[0:0, 0:] )
        s+= np.sum( data[-1:-1,0:] )
        return s

    def make_projection(self, axis, his, his_error):
        return np.sum( his, axis = axis),  np.sqrt( np.sum(his_error**2, axis=axis) )


    def get_fit_result(self, cfg):
        grids = get_coor_grid()
        coors = [grids['xc'],grids['yc']]
        data_field_names = [ 'data_sum', 'data_diff', 'fit_diff', 'fit_sum']

        data_field_dict = {}

        for field_name in data_field_names:
            this_data = getattr(self, field_name)

            if 'data' in field_name:
                this_data_type = 'dat'
                this_data_err = getattr(self,field_name + '_error')
            else:
                this_data_type = 'fit'
                this_data_err = np.zeros(this_data.shape)

            this_data_x, this_data_x_error = self.make_projection(0, this_data, this_data_err)
            this_data_y, this_data_y_error = self.make_projection(1, this_data, this_data_err)

            data_field_dict[field_name] = data_field (coors, this_data, this_data_err, label=field_name, data_type = this_data_type)

            data_field_dict[field_name+'_px'] = data_field( [grids['xc'], None], this_data_x, this_data_x_error, label= field_name+'_px', data_type = this_data_type)
            data_field_dict[field_name+'_py'] = data_field( [None, grids['yc']], this_data_y, this_data_y_error, label= field_name+'_py', data_type = this_data_type)


        data_field_dict['beam_shape']  = data_field( coors,  self.beam_shape, data_err = None, label='Reconstructed beam shape', data_type='dat')
        data_field_dict['beam_shape'].interpolation='bicubic'
        data_field_dict['beam_shape'].palette=plt.cm.magma

        data_field_dict['efficiency'] = data_field( coors,  self.efficiency, data_err = None, label='Relative efficiency', data_type='dat')
        data_field_dict['efficiency'].palette=plt.cm.seismic
        data_field_dict['efficiency'].interpolation='bicubic'

        data_field_dict['remains'] = data_field( coors,  self.remains, data_err = None, label='Remains', data_type='dat')
        data_field_dict['remains'].palette=plt.cm.seismic
        data_field_dict['remains'].interpolation='bicubic'

        interp='bicubic'
        #interp='none'
        data_field_dict['data_sum'].interpolation=interp
        data_field_dict['data_diff'].interpolation=interp
        data_field_dict['fit_diff'].interpolation=interp
        data_field_dict['fit_sum'].interpolation=interp

        data_field_dict['data_sum'].palette=plt.cm.magma
        data_field_dict['fit_sum'].palette=plt.cm.magma
        #data_field_dict['data_diff'].palette=plt.cm.viridis
        data_field_dict['data_diff'].palette=plt.cm.seismic
        data_field_dict['fit_diff'].palette=plt.cm.seismic
        #data_field_dict['data_diff'].palette=plt.cm.magma
        #data_field_dict['data_diff'].palette=plt.cm.coolwarm
        #data_field_dict['data_diff'].palette=plt.cm.PRGn
        return data_field_dict

    def fixpar(self, parname, value):
        self.minuit.values[parname]=value
        self.minuit.fixed[parname] = True
    
    def fit(self, cfg):
        par_ini = cfg['model_params']
        par_val = {k: par_ini[k][0] for k, v in par_ini.items() if par_ini[k][0] != '*'}
        par_err = {k: par_ini[k][1] for k, v in par_ini.items() if par_ini[k][1] != '*'}
        par_lim = {k: par_ini[k][2] for k, v in par_ini.items() if par_ini[k][2] != '*'}
        par_fix = {k: par_ini[k][3] for k, v in par_ini.items() }

        #print("Перед заданием начальных параметров")
        for parname in par_val.keys():
            self.minuit.values[parname] = par_val[parname]
        for parname in par_fix.keys():
            self.minuit.fixed[parname]  = par_fix[parname]
        for parname in par_err.keys():
            #print(parname, "err = " , par_err[parname])
            self.minuit.errors[parname] = par_err[parname]
        for parname in par_lim.keys():
            self.minuit.limits[parname] = par_lim[parname]

        print(self.minuit)

        self.Lerror = self.minuit.errors['L']
        self.L  = self.minuit.values['L']

        self.cb0 = np.zeros(self.ext_shape)
        self.cb1 = np.zeros(self.ext_shape)

        self.tied_VQ =  self.minuit.fixed['V'] and np.abs(self.minuit.values['V'])<0.00001
        #determine maximum in the sum of the left and right data
        self.N = 0.5*np.amax( self.raw_data_left + self.raw_data_right)

        #Должна быть предварительная подгонка для "расплывания" результата
        def migrad(k,psum=0.0):
            self.minuit.values['k']  = k 
            self.minuit.migrad()
            #self.minuit.values['psum']=psum
            self.cb0 = self.CB0.copy()
            self.cb1 = self.CB1.copy()

        self.minuit.fixed['k']=True
        for i in range(0,5):
            migrad(1e-5)

        self.minuit.strategy=2
        self.minuit.fixed['k']=par_fix['k']
        
        #Финальная подгонка
        migrad(par_val['k'],0.0)
        self.minuit.hesse()

        if self.tied_VQ:
            Q = self.minuit.values['Q']
            V = np.sqrt( 1.0 - Q**2)
            self.minuit.values['V']  = V
            self.minuit.errors['V'] = np.abs(Q/V*self.minuit.errors['Q']) 
        #print(dir(self.minuit))
        print(self.minuit.fmin) #Результат подгонки:EDM, сошлась-не сошлась
        print(self.minuit.params) #Печать полученных значений параметров в результате подгонки
        #Напечатать корреляционную матрицу
        #print(self.minuit.covariance.correlation())
        self.ndf = np.shape(self.x[0])[0]*np.shape(self.x[1])[0]-self.minuit.nfit
        self.chi2 = self.minuit.fval

        return self.minuit

