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
roman_bars = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX'}

name_dict = {'809BH': 'A', 'Altona': 'B', 'Locomo': 'C', 'Shilan': 'D'}
ht_samples = []
ac_samples = []
for heat in heats:
    for bar in bars[heat]:
        for cut in cuts:
            ht_samples.append('{:s}-{:d} {:d}ht'.format(heat, bar, cut))
            ac_samples.append('{:s}-{:d} {:d}ac'.format(heat, bar, cut))
            name_dict['{:s}-{:d} {:d}ht'.format(heat, bar, cut)] = '{:s}-{:s} {:d}ht'.format(heat, roman_bars[bar], cut)
            name_dict['{:s}-{:d} {:d}ac'.format(heat, bar, cut)] = '{:s}-{:s} {:d}ac'.format(heat, roman_bars[bar], cut)



#Density of inclusion per sample            
fig1 = analysis.dens_per_sample(commercial_samples)
fig2 = analysis.dens_per_sample(ht_samples)
fig2b = analysis.dens_per_sample(ac_samples)

#Feret diam per sample
fig3, ax = plt.subplots(3, 3)
fig3.subplots_adjust(hspace=0.4)

i=0
j=0
xlim=[2,100]

for heat in heats:
    for bar in bars[heat]:
        bar_ID = '{:s}-{:d}'.format(heat, bar)
        samples = []
        
        colors = ['C0', 'C1']
        for k in range(len(cuts)):
            sample = bar_ID + ' {:d}ht'.format(cuts[k])
            x, y = analysis.get_dens(sample, xlim=xlim)
            ax[i, j].semilogx(x, y, label = '{:d}ht'.format(cuts[k]), color = colors[k], linestyle = 'solid')
            
            sample = bar_ID + ' {:d}ac'.format(cuts[k])
            x, y = analysis.get_dens(sample, xlim=xlim)
            ax[i, j].semilogx(x, y, label = '{:d}ac'.format(cuts[k]), color = colors[k], linestyle = 'dashed')
            
            sample = bar_ID + ' {:d}ac'.format(cut)
            x, y = analysis.get_dens(sample, xlim=xlim)
            ax[i, j].semilogx(x, y, label = '{:d}ht'.format(cut))
            
        ax[i, j].set_xlabel('Feret diameter (\si{\micro\metre})')
        ax[i, j].set_ylabel('Inclusion density (\si{\per\micro\metre\per\milli\metre\squared})')
        ax[i, j].set_xlim(xlim)
        ax[i, j].legend()
        ax[i, j].set_title('{:s}-{:s}'.format(heat, roman_bars[bar]))
        
        if j==2:
            j=0
            i+=1
        else:
            j+=1

#Inclusion total area per sample
fig3b, ax = plt.subplots(3, 3)
fig3b.subplots_adjust(hspace=0.4)

i=0
j=0
xlim=[2,100]

for heat in heats:
    for bar in bars[heat]:
        bar_ID = '{:s}-{:d}'.format(heat, bar)
        samples = []
        
        colors = ['C0', 'C1']
        for k in range(len(cuts)):
            sample = bar_ID + ' {:d}ht'.format(cuts[k])
            x, y = analysis.get_dens(sample, xlim=xlim, weighted=True)
            ax[i, j].semilogx(x, y, label = '{:d}ht'.format(cuts[k]), color = colors[k], linestyle = 'solid')
            
            sample = bar_ID + ' {:d}ac'.format(cuts[k])
            x, y = analysis.get_dens(sample, xlim=xlim, weighted=True)
            ax[i, j].semilogx(x, y, label = '{:d}ac'.format(cuts[k]), color = colors[k], linestyle = 'dashed')
            
        ax[i, j].set_xlabel('Feret diameter (\si{\micro\metre})')
        ax[i, j].set_ylabel('Inclusion area density (\si{\per\micro\metre \micro\metre\squared\per\milli\metre\squared})')
        ax[i, j].set_xlim(xlim)
        ax[i, j].legend()
        ax[i, j].set_title('{:s}-{:s}'.format(heat, roman_bars[bar]))
        
        if j==2:
            j=0
            i+=1
        else:
            j+=1

        
#Average distribution per sample - commercial samples
fig4, ax = plt.subplots(1, 2)
for sample in commercial_samples:
    x, y = analysis.get_dens(sample, xlim = xlim)
    ax[0].semilogx(x, y, label = name_dict[sample])
    x2, y2 = analysis.get_dens(sample, xlim = xlim, weighted=True)
    ax[1].semilogx(x2, y2, label = name_dict[sample])

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
        ax[0].semilogx(x, y, label = '{:s}-{:s}'.format(heat, roman_bars[bar]))
        
        x, y1 = analysis.get_dens(samples[0], xlim=xlim, weighted=True)
        x, y2 = analysis.get_dens(samples[1], xlim=xlim, weighted=True)
        y = (y1 + y2)/2
        ax[1].semilogx(x, y, label = '{:s}-{:s}'.format(heat, roman_bars[bar]))

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

#Average distribution per sample - as-cast samples
fig6, ax = plt.subplots(1, 2)
for heat in heats:
    for bar in bars[heat]:
        bar_ID = '{:s}-{:d}'.format(heat, bar)
        samples = []
        for cut in cuts:
            samples.append(bar_ID + ' {:d}ac'.format(cut))
        
        x, y1 = analysis.get_dens(samples[0], xlim=xlim)
        x, y2 = analysis.get_dens(samples[1], xlim=xlim)
        y = (y1 + y2)/2
        ax[0].semilogx(x, y, label = '{:s}-{:s}'.format(heat, roman_bars[bar]))
        
        x, y1 = analysis.get_dens(samples[0], xlim=xlim, weighted=True)
        x, y2 = analysis.get_dens(samples[1], xlim=xlim, weighted=True)
        y = (y1 + y2)/2
        ax[1].semilogx(x, y, label = '{:s}-{:s}'.format(heat, roman_bars[bar]))

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


#Average distribution per sample - square root area parameter - heat-treated samples
fig7, ax = plt.subplots(1, 2)
for heat in heats:
    for bar in bars[heat]:
        bar_ID = '{:s}-{:d}'.format(heat, bar)
        samples = []
        for cut in cuts:
            samples.append(bar_ID + ' {:d}ac'.format(cut))
        
        x, y1 = analysis.get_dens(samples[0], xlim=xlim, param='sqr_area')
        x, y2 = analysis.get_dens(samples[1], xlim=xlim, param='sqr_area')
        y = (y1 + y2)/2
        ax[0].semilogx(x, y, label = '{:s}-{:s}'.format(heat, roman_bars[bar]))
        
        x, y1 = analysis.get_dens(samples[0], xlim=xlim, weighted=True, param='sqr_area')
        x, y2 = analysis.get_dens(samples[1], xlim=xlim, weighted=True, param='sqr_area')
        y = (y1 + y2)/2
        ax[1].semilogx(x, y, label = '{:s}-{:s}'.format(heat, roman_bars[bar]))

ax[0].set_xlim(xlim)
ax[0].legend()
ax[0].set_xlabel('Square root area $\sqrt{A}$ (\si{\micro\metre})')
ax[0].set_ylabel('Inclusion count density (\si{\per\micro\metre\per\milli\metre\squared})')
ax[0].set_title('Inclusion count')
ax[1].set_xlim(xlim)
ax[1].legend()
ax[1].set_xlabel('Square root area $\sqrt{A}$ (\si{\micro\metre})')
ax[1].set_ylabel('Inclusion area density (\si{\per\micro\metre \micro\metre\squared\per\milli\metre\squared})')
ax[1].set_title('Inclusion area')

#Average distribution per sample - commercial samples
fig8, ax = plt.subplots(1, 2)
for sample in commercial_samples:
    x, y = analysis.get_dens(sample, xlim = xlim, param = 'sqr_area')
    ax[0].semilogx(x, y, label = name_dict[sample])
    x2, y2 = analysis.get_dens(sample, xlim = xlim, weighted=True, param='sqr_area')
    ax[1].semilogx(x2, y2, label = name_dict[sample])

ax[0].set_xlim(xlim)
ax[0].legend()
ax[0].set_xlabel('Square root area $\sqrt{A}$ (\si{\micro\metre})')
ax[0].set_ylabel('Inclusion count density (\si{\per\micro\metre\per\milli\metre\squared})')
ax[0].set_title('Inclusion count')
ax[1].set_xlim(xlim)
ax[1].legend()
ax[1].set_xlabel('Square root area $\sqrt{A}$ (\si{\micro\metre})')
ax[1].set_ylabel('Inclusion area density (\si{\per\micro\metre \micro\metre\squared\per\milli\metre\squared})')
ax[1].set_title('Inclusion area')