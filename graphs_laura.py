import analysis

#Configuration of Matplotlib grahps to use LaTeX formatting with siunitx library
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import matplotlib as mpl
from matplotlib import rc
rc('font',**{'family':'serif','serif':['DejaVu Sans']})
rc('text', usetex=True)
mpl.rcParams['errorbar.capsize'] = 3
mpl.rcParams['lines.markersize'] = 5
mpl.rcParams['text.latex.preamble']=r'\usepackage{siunitx}'

commercial_samples = ['809BH', 'Altona', 'Locomo', 'Shilan']
heats = ['2019C', '2020C', '2019V', '2020V']
bars = {'2019C': [1], '2020C': [1, 2], '2019V': [1], '2020V': [2, 6, 7, 8, 9]}
cuts = [1, 2]

ht_samples = []
for heat in heats:
    for bar in bars[heat]:
        for cut in cuts:
            ht_samples.append('{:s}-{:d} {:d}ht'.format(heat, bar, cut))


#Density of inclusion per sample            
fig1 = analysis.dens_per_sample(commercial_samples)
fig2 = analysis.dens_per_sample(ht_samples)

#Feret diam per sample
fig3, ax = plt.subplots(3, 3)
fig3.subplots_adjust(hspace=0.4)

i=0
j=0
xlim=[0,100]

for heat in heats:
    for bar in bars[heat]:
        bar_ID = '{:s}-{:d}'.format(heat, bar)
        samples = []
        for cut in cuts:
            sample = bar_ID + ' {:d}ht'.format(cut)
            x, y = analysis.get_dens(sample, xlim=xlim)
            ax[i, j].semilogx(x, y, label = '{:d}ht'.format(cut))
            
        ax[i, j].set_xlabel('Feret diameter (\si{\micro\metre})')
        ax[i, j].set_ylabel('Inclusion density (\si{\per\micro\metre\per\milli\metre\squared})')
        ax[i, j].set_xlim(xlim)
        ax[i, j].legend()
        ax[i, j].set_title(bar_ID)
        
        if j==2:
            j=0
            i+=1
        else:
            j+=1

        
fig3, ax = plt.subplots(3, 3)
fig3.subplots_adjust(hspace=0.4)

i=0
j=0
xlim=[2,100]

for heat in heats:
    for bar in bars[heat]:
        bar_ID = '{:s}-{:d}'.format(heat, bar)
        samples = []
        for cut in cuts:
            sample = bar_ID + ' {:d}ht'.format(cut)
            x, y = analysis.get_dens(sample, xlim=xlim)
            ax[i, j].semilogx(x, y, label = '{:d}ht'.format(cut))
            
        ax[i, j].set_xlabel('Feret diameter (\si{\micro\metre})')
        ax[i, j].set_ylabel('Inclusion density (\si{\per\micro\metre\per\milli\metre\squared})')
        ax[i, j].set_xlim(xlim)
        ax[i, j].legend()
        ax[i, j].set_title(bar_ID)
        
        if j==2:
            j=0
            i+=1
        else:
            j+=1
        
#Average distribution per sample - commercial samples
fig4, ax = plt.subplots(1, 2)
for sample in commercial_samples:
    x, y = analysis.get_dens(sample, xlim = xlim)
    ax[0].semilogx(x, y, label = sample)
    x2, y2 = analysis.get_dens(sample, xlim = xlim, weighted=True)
    ax[1].semilogx(x2, y2, label = sample)

ax[0].set_xlim(xlim)
ax[0].legend()
ax[0].set_xlabel('Feret diameter (\si{\micro\metre})')
ax[0].set_ylabel('Inclusion count density (\si{\per\micro\metre\per\milli\metre\squared})')
ax[0].set_title('Inclusion count')
ax[1].set_xlim(xlim)
ax[1].legend()
ax[1].set_xlabel('Feret diameter (\si{\micro\metre})')
ax[1].set_ylabel('Inclusion area density (\si{\per\micro\metre \micro\metre\squared\per\milli\metre\squared})')
ax[1].set_title('Inclusion area')

        
#Average distribution per sample - heat-treated samples
fig5, ax = plt.subplots(1, 2)
for heat in heats:
    for bar in bars[heat]:
        bar_ID = '{:s}-{:d}'.format(heat, bar)
        samples = []
        for cut in cuts:
            samples.append(bar_ID + ' {:d}ht'.format(cut))
        
        x, y1 = analysis.get_dens(samples[0], xlim=xlim)
        x, y2 = analysis.get_dens(samples[1], xlim=xlim)
        y = (y1 + y2)/2
        ax[0].semilogx(x, y, label = bar_ID)
        
        x, y1 = analysis.get_dens(samples[0], xlim=xlim, weighted=True)
        x, y2 = analysis.get_dens(samples[1], xlim=xlim, weighted=True)
        y = (y1 + y2)/2
        ax[1].semilogx(x, y, label = bar_ID)

ax[0].set_xlim(xlim)
ax[0].legend()
ax[0].set_xlabel('Feret diameter (\si{\micro\metre})')
ax[0].set_ylabel('Inclusion count density (\si{\per\micro\metre\per\milli\metre\squared})')
ax[0].set_title('Inclusion count')
ax[1].set_xlim(xlim)
ax[1].legend()
ax[1].set_xlabel('Feret diameter (\si{\micro\metre})')
ax[1].set_ylabel('Inclusion area density (\si{\per\micro\metre \micro\metre\squared\per\milli\metre\squared})')
ax[1].set_title('Inclusion area')