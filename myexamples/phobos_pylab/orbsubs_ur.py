
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import median_filter
from numpy import linalg as LA
#from matplotlib import rc
#rc('text', usetex=True)
from numpy import polyfit
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from math import fmod
from scipy.signal import medfilt

from kepcart import *
from outils import * # useful short routines

angfac = 180.0/np.pi # for converting radians to degrees
twopi = np.pi*2.0

def residual(ang):
    z = fmod(ang,twopi)
    if (z < 0):
        z = z+ twopi
    return z

def residual_vec(angvec):
    nvec = len(angvec)
    mvec = angvec*0.0
    for i in range(0,nvec):
        mvec[i] = residual(angvec[i])
    return mvec


# read in a pointmass file  format fileroot_pm0.txt
def readpmfile(fileroot,npi):
    junk = '.txt'
    filename = "%s_pm%d%s"%(fileroot,npi,junk)
    print(filename)
    tt,x,y,z,vx,vy,vz,mm =\
           np.loadtxt(filename, skiprows=1, unpack='true') 
    return tt,x,y,z,vx,vy,vz,mm

# read in an extended mass output  file  format fileroot_ext.txt
def readresfile(fileroot):
    filename = fileroot+'_ext.txt'
    print(filename)
    t,x,y,z,vx,vy,vz,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz,KErot,PEspr,PEgrav,Etot,dEdt =\
        np.loadtxt(filename, skiprows=1, unpack='true') 
    return t,x,y,z,vx,vy,vz,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz,KErot,PEspr,PEgrav,Etot,dEdt


# read in all the point mass files at once
# return a mass array
# return time array
# return tuple of position and velocity vectors?
def readallpmfiles(fileroot,numberpm):
    mvec = np.zeros(0)    
    tt,x,y,z,vx,vy,vz,mm=readpmfile(fileroot,0)
    nt = len(tt)  # length of arrays
    mvec = np.append(mvec,mm[0])
    xarr = np.zeros((numberpm,nt))
    yarr = np.zeros((numberpm,nt))
    zarr = np.zeros((numberpm,nt))
    vxarr = np.zeros((numberpm,nt))
    vyarr = np.zeros((numberpm,nt))
    vzarr = np.zeros((numberpm,nt))
    xarr[0] = x
    yarr[0] = y
    zarr[0] = z
    vxarr[0] = vx
    vyarr[0] = vy
    vzarr[0] = vz
    for i in range(1,numberpm):
        ttt,x,y,z,vx,vy,vz,mm=readpmfile(fileroot,i)
        mvec = np.append(mvec,mm[0])
        xarr[i] = x
        yarr[i] = y
        zarr[i] = z
        vxarr[i] = vx
        vyarr[i] = vy
        vzarr[i] = vz

    return tt, mvec, xarr,yarr,zarr,vxarr,vyarr,vzarr

# limit the number of points plotted to this
plmax = 5000   # max number of points for arrays

# fill arrays with orbital elements all w.r.t to first point mass
# which is assumed to be the central object
# resolved body orbit is put in first index of arrays
# computes obliquity,spin,J also 
def orbels_arr(fileroot,numberpm):
    t,x,y,z,vx,vy,vz,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz,KErot,PEspr,PEgrav,Etot,dEdt=\
       readresfile(fileroot)  # resolved body stuff
    tt, mvec, xarr,yarr,zarr,vxarr,vyarr,vzarr=\
       readallpmfiles(fileroot,numberpm)  # point mass stuff
    imc = 0  # index of central mass
    GM = mvec[imc]   #+1 possibly?
    # print('GM',GM);
    nl = len(tt)
    kk = np.int(nl/plmax)    # reduce array sizes by this interval!
    if (kk<1): 
        kk=1
    ts = t[0::kk]  # short time array
    print("kk=",kk);
    # coordinates with respect to first point mass that is assumed to be central object
    dxarr = x- xarr[imc];  dyarr= y- yarr[imc];  dzarr= z- zarr[imc]
    dvxarr=vx-vxarr[imc]; dvyarr=vy-vyarr[imc]; dvzarr=vz-vzarr[imc]
    # reduce array size
    dxarr = dxarr[0::kk];    dyarr =  dyarr[0::kk];  dzarr =  dzarr[0::kk]
    dvxarr = dvxarr[0::kk]; dvyarr = dvyarr[0::kk]; dvzarr = dvzarr[0::kk]
    ns = len(dxarr)
    #print(ns)
    xarrs = np.zeros((numberpm,ns))
    #print(len(xarrs[0]))
    aaarr = xarrs*0.0; eearr = xarrs*0.0; iiarr = xarrs*0.0;
    lnarr = xarrs*0.0; ararr = xarrs*0.0; maarr = xarrs*0.0;
    #
    # compute orbital elements for the resolved body assuming w.r.t to central mass set by imc
    for k in range(ns):      # for the resolved body
        aa,ee,ii,longnode,argperi,meananom=\
               keplerian(GM+1,dxarr[k],dyarr[k],dzarr[k],dvxarr[k],dvyarr[k],dvzarr[k])
        aaarr[imc][k] = aa
        eearr[imc][k] = ee
        iiarr[imc][k] = ii
        lnarr[imc][k] = longnode
        ararr[imc][k] = argperi 
        maarr[imc][k] = meananom 
    # mms =np.sqrt(GM*aaarr[imc,0]**-3) # mean motion of resolved to check!
    # print('mean motion', mms) 

    omxs = omx[0::kk]; llxs = llx[0::kk];  # spins and spin angular momentums
    omys = omy[0::kk]; llys = lly[0::kk];
    omzs = omz[0::kk]; llzs = llz[0::kk];
    Ixxs = Ixx[0::kk]; Iyys = Iyy[0::kk]; Izzs = Izz[0::kk]; # moments of inertia
    Ixys = Ixy[0::kk]; Iyzs = Iyz[0::kk]; Ixzs = Ixz[0::kk];
    no_x,no_y,no_z=crossprod_unit(dxarr,dyarr,dzarr,dvxarr,dvyarr,dvzarr)  #orbit normal
    nlx,nly,nlz = normalize_vec(llxs,llys,llzs) # body spin angular momentum unit vector

    # compute obliquity, angle between body spin angular momentum and orbit normal
    ang_so = dotprod(nlx,nly,nlz,no_x,no_y,no_z)
    ang_so = np.arccos(ang_so)*angfac   # obliquity  in degrees
    obliquity_deg = ang_so
    spin = len_vec(omxs,omys,omzs)
    # compute a bunch of angles for body w.r.t to spin and angular momentum vectors
    tvec_b,svec_ma,lvec_ma,svec_mi,lvec_mi,svec_me,lvec_me,ang_ll,gdot,ldot,\
            lam1dot, spinvec=\
            vec_tilts(1,ts,omxs,omys,omzs,llxs,llys,llzs,Ixxs,Iyys,Izzs,Ixys,Iyzs,Ixzs)
    Jvec = lvec_ma  # angle between angular momentum and principal body axis
    # Jvec is an NPA angle!
    prec_ang=precess_ang(llxs,llys,llzs,1.0,0.0,0.0,0.0,1.0,0.0)
    # precession angle w.r.t to xyz coordinate system, given are x and y vectors assuming
    # that they are similar to the orbital plane

    # for point masses compute orbital elements, w.r.t to imc as central one
    for i in range(1,numberpm):
        dxarr = xarr[i]- xarr[imc];  dyarr= yarr[i] -  yarr[imc];  dzarr= zarr[i]- zarr[imc]
        dvxarr=vxarr[i]-vxarr[imc]; dvyarr=vyarr[i] - vyarr[imc]; dvzarr=vzarr[i]-vzarr[imc]
        dxarr   = dxarr[0::kk];  dyarr =  dyarr[0::kk];  dzarr =  dzarr[0::kk]
        dvxarr = dvxarr[0::kk]; dvyarr = dvyarr[0::kk]; dvzarr = dvzarr[0::kk]
        for k in range(ns):    # for the point masses  
            dx  =  xarr[i][k] -  xarr[imc][k]
            dy  =  yarr[i][k] -  yarr[imc][k]
            dz  =  zarr[i][k] -  zarr[imc][k]
            dvx = vxarr[i][k] - vxarr[imc][k]
            dvy = vyarr[i][k] - vyarr[imc][k]
            dvz = vzarr[i][k] - vzarr[imc][k]
            aa,ee,ii,longnode,argperi,meananom=\
               keplerian(GM +mvec[i],dxarr[k],dyarr[k],dzarr[k],dvxarr[k],dvyarr[k],dvzarr[k])
            aaarr[i][k] = aa
            eearr[i][k] = ee
            iiarr[i][k] = ii
            lnarr[i][k] = longnode
            ararr[i][k] = argperi 
            maarr[i][k] = meananom 

    # compute body orientation angle of principal axis in xyplane
    # and body tilt w.r.t to z axis
    phi_Eu = spin*0.0
    theta_Eu = spin*0.0
    bphi_Eu = spin*0.0
    for k in range(ns):  # vmin corresponds to long axis of body, vmax to shortest axis
       vmax,vmin,vmed = evec(k,Ixxs,Iyys,Izzs,Ixys,Iyzs,Ixzs)  # eigenvectors are body orientation axes
       phi_Eu[k] = np.arctan2(vmin[1],vmin[0]);  # an Euler angle, w.r.t to xyz coord system
       # angle of body major axis on xy plane
       # xy, orientation of body major axis gives this angle
       theta_Eu[k] = np.arccos(vmax[2]);  # another Euler angle
       # angle of body minor axis w.r.t to z axis
       bphi_Eu[k] = np.arctan2(vmax[1],vmax[0]);  # another angle
       # angle of body minor axis on xy plane 

    I3,I2,I1= I3I2I1(0,Ixxs,Iyys,Izzs,Ixys,Iyzs,Ixzs)
    print("I3I2I1 ",I3,I2,I1);
    gam = (I2-I1)/I3  # (B-A)/C
    alpha = np.sqrt(3.0*(I2-I1)/I3)  # sqrt(3*(B-A)/C) = sqrt(3gamma)asphericity parm for libr
    qeff = (I3 - (I1 + I2)/2)/I3   # [C - (A+B)/2]/C for wobble
    print("alpha(lib)=",alpha, " qeff(wobble)=",qeff, " gam =",gam);
    I3,I2,I1= I3I2I1(len(Ixxs)-1,Ixxs,Iyys,Izzs,Ixys,Iyzs,Ixzs)
    print("I3I2I1 ",I3,I2,I1);
    gam = (I2-I1)/I3  # (B-A)/C
    alpha = np.sqrt(3.0*(I2-I1)/I3)  # sqrt(3*(B-A)/C) = sqrt(3gamma)asphericity parm for libr
    qeff = (I3 - (I1 + I2)/2)/I3   # [C - (A+B)/2]/C for wobble
    print("alpha(lib)=",alpha, " qeff(wobble)=",qeff, " gam =",gam);
   
   
    Etots = Etot[0::kk]
    dEdts = dEdt[0::kk]
    Ivec =(I3,I2,I1)

    return ts,mvec,aaarr,eearr,iiarr,lnarr,ararr,maarr,obliquity_deg,spin,Jvec,prec_ang,\
            phi_Eu,theta_Eu,bphi_Eu,dEdts,Ivec


# not used in this file
# computes obliquity,spin,J 
def give_body_angs(fileroot):
    # angle between body angular momentum and orbit normal
    t,x,y,z,vx,vy,vz,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz,KErot,PEspr,PEgrav,Etot,dEdt=\
       readresfile(fileroot)  # resolved body stuff
    numberpm=1
    tt, mvec, xarr,yarr,zarr,vxarr,vyarr,vzarr=\
       readallpmfiles(fileroot,numberpm)  # point mass read in stuff
    # normal to orbit
    imc = 0  # central mass, assume that this is the 
    dx = x - xarr[imc]; dvx = vx - vxarr[imc]
    dy = y - yarr[imc]; dvy = vy - vyarr[imc]
    dz = z - zarr[imc]; dvz = vz - vzarr[imc]
    no_x,no_y,no_z=crossprod_unit(dx,dy,dz,dvx,dvy,dvz)  #orbit normal
    nlx,nly,nlz = normalize_vec(llx,lly,llz)  # body spin angular momentum unit vect
    ang_so = dotprod(nlx,nly,nlz,no_x,no_y,no_z)
    ang_so = np.arccos(ang_so)*angfac   # obliquity  in degrees
    obliquity_deg = ang_so
    spin = len_vec(omx,omy,omz)
    # see tilts() on what this computes
    kb=1  # every 
    tvec_b,svec_ma,lvec_ma,svec_mi,lvec_mi,svec_me,lvec_me,ang_ll,gdot,ldot,\
            lam1dot, spinvec=\
            vec_tilts(kb,t,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz)
    Jvec = lvec_ma  # angle between angular momentum and principal body axis
    return obliquity_deg,spin,Jvec


## jj is resonance index for jj+dj:jj resonance
def plt_cols(fileroot,numberpm,saveit,tmin,tmax,jj,dj):
    tt,mvec,aaarr,eearr,iiarr,lnarr,ararr,maarr,obliq_deg,spin,Jvec,prec_ang,phi_Eu,theta_Eu,bphi_Eu,dEdt,Ivec=\
       orbels_arr(fileroot,numberpm)
    varpi = lnarr + ararr
    meanlongitude = varpi + maarr
    # get orbels of second point mass in terms of com of resolved and first body
    #ts,aaarr_p,eearr_p,iiarr_p,lnarr_p,ararr_p,maarr_p = orbel_com(fileroot,numberpm,1)
    #varpi_p = lnarr_p + ararr_p; meanlongitude_p = varpi_p + maarr_p
    ###
    sGM = np.sqrt(mvec[0])
    #
    ###########set up figure
    #plt.rcParams.update({'font.size': 14})
    nvpanels=6
    f,axarr =  plt.subplots(nvpanels,2, dpi=100, figsize=(11,8), sharex=True)
    plt.autoscale(enable=True, axis='x', tight=True)
    plt.subplots_adjust(left=0.09, right=0.99, top=0.99, bottom=0.10, \
        wspace=0.22, hspace=0.0)
    xmin = 0.0; xmax = np.max(tt)
    iimin = 0
    if (tmax > 0):
        xmax = np.min([xmax,tmax])
    if (tmin > 0):
        xmin = tmin;  
        iimin = np.argmin(abs(tmin-tt))
    mm0 = (mvec[0]+1)**0.5*aaarr[0]**-1.5  # mean motion 

    colorstr = ['k', 'r', 'b', 'g', 'm', 'c']
    ncolors = len(colorstr)

    il = 0; ih=0  # top left
    axarr[il,ih].set_ylabel('obliquity (deg)')
    axarr[il,ih].plot(tt,obliq_deg,'c.', ms=2) # label='')
    axarr[il,ih].set_xlim([xmin,xmax])

    il = 1; ih=0  # second left
    axarr[il,ih].set_ylabel('a e')
    for ip in range(numberpm):
        colorl = colorstr[ip%ncolors]
        ytop = aaarr[ip]*eearr[ip]                                       ## ee err
        ybot = ytop             
        if (max(aaarr[ip])<300):
           axarr[il,ih].scatter(tt,aaarr[ip],color=colorl, s=1) # label='') # aa
           axarr[il,ih].errorbar(tt,aaarr[ip],yerr=[ybot,ytop],\
               linestyle="None", marker="None", color=colorl)

    #axarr[il,ih].set_ylim(0,50);

    il = 2; ih=0  # third  left
    if (numberpm >1):
        #axarr[il,ih].set_ylabel('res angle')
        #jj = 5.0 # resonant index #dj = 2.0 # resonant index
        aav0 = np.mean(aaarr[0]);
        aav1 = np.mean(aaarr[1]);
        if (aav0 > aav1):
            resang = residual_vec(jj*meanlongitude[0] - dj*meanlongitude[1] - dj*varpi[0])
        else:
            resang = residual_vec(jj*meanlongitude[1] - dj*meanlongitude[0] - (jj-dj)*varpi[1])
        #resang = residual_vec(3*meanlongitude[1] - meanlongitude[0] - dj*varpi[1])
        #axarr[il,ih].plot(tt,resang,'.', color='purple',ms=2) # label='')
        #axarr[il,ih].set_ylim([0.0,2.0*np.pi])

    esmo = medfilt(dEdt,101)
    i0=0; i1=0
    if (len(dEdt)>  500):
        i0=200
        i1=len(dEdt) - 101
    axarr[il,ih].plot(tt[i0:i1],np.log10(esmo[i0:i1]+1e-10),',', color='gray',ms=1);
    axarr[il,ih].set_ylabel('log10 dEdt')
    ax_r = axarr[il,ih].twinx()
    try1 = np.log10(esmo+1e-10) +  7.5*np.log10(abs(aaarr[0]))
    ax_r.plot(tt[i0:i1],try1[i0:i1],',', color='violet',ms=1);

    il = 3; ih=0  # fourth left 
    #axarr[il,ih].set_ylabel('Oms-varpi_p')
    #domega = residual_vec(prec_ang-ararr[1])
    axarr[il,ih].set_ylabel('Jvec deg')
    Jvec_deg = Jvec%np.pi *180./np.pi;
    axarr[il,ih].plot(tt,Jvec_deg,'.', color='cornflowerblue',ms=2) # label='')
    axarr[il,ih].set_ylim([0.0,max(Jvec_deg)])

    il = 4; ih=0  # fifth left 
    axarr[il,ih].set_ylabel('inclinations (deg)')
    for ip in range(numberpm):
        colorl = colorstr[ip%ncolors]
        axarr[il,ih].scatter(tt,iiarr[ip]*180.0/np.pi,color=colorl, s=1) # label='')

    il = 5; ih=0  # sixth left 
    if (numberpm >1):
      axarr[il,ih].set_ylabel('some angle')
      #some_ang = residual_vec(lnarr[0] + meanlongitude[1]);
      #some_ang2 = residual_vec(lnarr[0]*2 + meanlongitude[1]);
      some_ang  = residual_vec(3*prec_ang- 1*lnarr[0]);
      #axarr[il,ih].plot(tt,some_ang,'.', color='orange',ms=1);
      #some_ang2 = residual_vec(2*prec_ang - lnarr[0]);
      some_ang2 = residual_vec(phi_Eu - meanlongitude[1]);
      #axarr[il,ih].plot(tt,some_ang2,'.', color='grey',ms=1);
      #some_ang3  = residual_vec(4*prec_ang- 1*lnarr[0]);
      #axarr[il,ih].plot(tt,some_ang3,'.', color='lightgreen',ms=1);
      some_ang3  = residual_vec(phi_Eu - 1*meanlongitude[0] + 1*meanlongitude[1]);
      axarr[il,ih].plot(tt,some_ang3,'.', color='darkgreen',ms=1);
      some_ang4  = residual_vec(phi_Eu - 2*meanlongitude[0] + 1*meanlongitude[1]);
      axarr[il,ih].plot(tt,some_ang4,'.', color='lightgreen',ms=1);

    il = 0; ih=1  # top right
    axarr[il,ih].set_ylabel('spin')
    spinmin = np.min(spin)
    spinmax = np.max(spin[iimin:])
    axarr[il,ih].set_ylim([spinmin-0.01,spinmax+0.01])
    ares = aaarr[0]
    nres = sGM/abs(ares)**1.5
    nres_min = np.min(nres)
    kmax = np.int(2*spinmax/nres_min)
    for i in range(0,kmax+2):
       axarr[il,ih].plot(tt,nres*i/2,'.', color="pink",ms=2)
    axarr[il,ih].plot(tt,spin,'.', color='green',ms=2) # label='')

    il = 1; ih=1  # second right
    axarr[il,ih].set_ylabel('Oms-Om')
    domega = residual_vec(prec_ang-lnarr[0])
    axarr[il,ih].plot(tt,residual_vec(lnarr[0]),'.', color='grey',ms=1) # label='')
    axarr[il,ih].plot(tt,residual_vec(prec_ang),'.', color='pink',ms=1)
    #axarr[il,ih].plot(tt,residual_vec(meanlongitude[1]),'.', color='orange',ms=1)
    #axarr[il,ih].plot(tt,residual_vec(varpi[0]),'.', color='orange',ms=1)
    #angtry = residual_vec(prec_ang+varpi[0])
    #angtry2 = residual_vec(prec_ang-varpi[0])
    angtry = residual_vec(prec_ang-lnarr[0]*2)
    angtry2 = residual_vec(prec_ang-lnarr[0]*2-varpi[0])
    #axarr[il,ih].plot(tt,angtry,'.', color='cyan',ms=1) # label='')
    #axarr[il,ih].plot(tt,angtry2,'.', color='orange',ms=1) # label='')
    some_ang2 = residual_vec(bphi_Eu - lnarr[0]);
    axarr[il,ih].plot(tt,some_ang2,'.', color='red',ms=1);
    axarr[il,ih].plot(tt,domega,'.', color='blue',ms=2) # label='')
    axarr[il,ih].set_ylim([0.0,2.0*np.pi])


    il = 2; ih=1  # third  right
    #domega = residual_vec(prec_ang-ararr[0])
    #axarr[il,ih].plot(tt,domega,'.', color='darkred',ms=2) # label='')
    #axarr[il,ih].set_ylabel('Oms-varpi')
    phi_Eu_res = residual_vec(phi_Eu - meanlongitude[0]) 
    theta_Eu_res = residual_vec(theta_Eu)%np.pi;
    axarr[il,ih].plot(tt,theta_Eu_res,'.', color='darkgreen',ms=2) # label='')
    axarr[il,ih].plot(tt,phi_Eu_res,'.', color='darkred',ms=2) # label='')
    axarr[il,ih].set_ylabel(r'$\phi_{Eu} - \lambda, \theta_{Eu}$')
    axarr[il,ih].set_ylim([ 0.0*np.pi,1.0*np.pi])

    #il = 3; ih=1  # fourth  right
    #resang = residual_vec(jj*meanlongitude[0] - (jj+1)*meanlongitude[1] + prec_ang)
    #axarr[il,ih].plot(tt,resang,'.', color='brown',ms=2) # label='')
    #axarr[il,ih].set_ylim([0.0,2.0*np.pi])
    #axarr[il,ih].set_ylabel('res angle Oms')

    il = 3; ih=1  # fourth  right
    axarr[il,ih].set_ylabel('P ratio')
    ax_r = axarr[il,ih].twinx()
    for ip in range(1,numberpm):
        colorl = colorstr[ip%ncolors]
        mrat = np.sqrt(mvec[0]/(mvec[0] + mvec[ip]))
        pratio = (aaarr[ip]/aaarr[ip-1])**1.5 * mrat
        r_rat = 60.2*(12/pratio)**0.6667
        pmean = np.mean(pratio)
        if (pmean < 1):
            pratio = 1.0/pratio
        axarr[il,ih].scatter(tt,pratio,color=colorl, s=1) # label='')
        ax_r.scatter(tt,r_rat,color='orange', s=1) # label='')


    il = 4; ih=1  # fifth   right
    axarr[il,ih].set_ylabel('eccentricities')
    for ip in range(numberpm):
        colorl = colorstr[ip%ncolors]
        axarr[il,ih].scatter(tt,eearr[ip],color=colorl, s=1) # label='')

    il = 5; ih=1  # sixth  right
    if (numberpm >1):
       mm1 = mvec[1]**0.5*aaarr[1]**-1.5  # mean motion 
       mratio = mm1/mm0
    Rplus =1.5
    J2=0.03
    prf = 1.5*J2*(Rplus/aaarr[0])**2 # ratio of precession freq
    axarr[il,ih].plot(tt,mm0,'.',color='gray',ms=1);
    axarr[il,ih].plot(tt,prf,'.',color='gray',ms=1);
    # axarr[il,ih].plot(tt,prf/2,'.',color='red',ms=1);
    if (numberpm >1):
       axarr[il,ih].plot(tt,mratio,'.',color='blue',ms=1);
    #axarr[il,ih].plot(tt,mm1,'.',color='darkblue',ms=1);
    I3 = Ivec[0]; I2 = Ivec[1]; I1 = Ivec[2]
    gam = (I2-I1)/I3
    alpha = np.sqrt(3.0*(I2-I1)/I3)  # sqrt(3*(B-A)/C) = sqrt(3gamma)asphericity parm for libr
    qeff = (I3 - (I1 + I2)/2)/I3   # [C - (A+B)/2]/C for wobble
    #print("alpha(lib)=",alpha, " qeff(wobble)=",qeff, " gam =",gam);
    #axarr[il,ih].plot(tt,alpha + tt*0,'.',color='green',ms=1);
    axarr[il,ih].plot(tt,qeff + tt*0,'.',color='orange',ms=1);


    plt.ticklabel_format(axis='x', style='sci', scilimits=(-2,2))
    il = nvpanels-1; ih=0; axarr[il,ih].set_xlabel('time')
    il = nvpanels-2; ih=1; axarr[il,ih].set_xlabel('time')



# not used
# make an inertial coordinate system, numbers not vectors returned
# total angular momentum is nearly fixed
def ntvec(lx,ly,lz,lox,loy,loz):
    lt_x = lx[0] + lox[0];  #sum the angular momentum of spin and orbit
    lt_y = ly[0] + loy[0];
    lt_z = lz[0] + loz[0];
    lt = len_vec(lt_x,lt_y,lt_z)
    nt_x = lt_x/lt  # unit vector
    nt_y = lt_y/lt
    nt_z = lt_z/lt
    #print("nt=",nt_x,nt_y,nt_z)   # unit vector in total ang momentum direction
    return nt_x,nt_y,nt_z  

# not used
# returns two vectors perpendicular to total angular momentum (or given vector)
# the given vector give need not be normalized
# one of the vectors returned is near x axis
# the two vectors returned are normalized and perpendicular to each other
def exy(nt_x,nt_y,nt_z):
    ex_x,ex_y,ex_z = aperp(1.0,0.0,0.0,nt_x,nt_y,nt_z)  # a vector near x
    ex_x,ex_y,ex_z = normalize_vec(ex_x,ex_y,ex_z)  #normalize
    #print ("ex=",ex_x,ex_y,ex_z)
    ey_x, ey_y, ey_z = crossprod_unit(nt_x,nt_y,nt_z,ex_x,ex_y,ex_z)
    #print ("ey=",ey_x,ey_y,ey_z)
    return  ex_x,ex_y,ex_z,ey_x,ey_y,ey_z


# project spin angular momentum onto ex,ey, vectors 
# lx,ly,lz can be arrays 
def precess_ang(lx,ly,lz,ex_x,ex_y,ex_z,ey_x,ey_y,ey_z):
    xproj = dotprod(lx,ly,lz,ex_x,ex_y,ex_z)
    yproj = dotprod(lx,ly,lz,ey_x,ey_y,ey_z)
    prec_ang = np.arctan2(yproj,xproj)
    return prec_ang


# median filter an angle (like the precession angle), returing precession rate, cleaned
def prec_dphidt(tt,prec_ang,boxsize):
    dt = tt[1] - tt[0]
    nn = np.size(tt)
    dphidt =np.diff(prec_ang)/dt  # precession rate
    dphidt =np.append(dphidt,dphidt[nn-2])# so array the same size all others 
    mf = median_filter(dphidt,boxsize)
    return mf

    
# at index j from moments of inertia arrays
# return eigenvector of max eigen value 
#    and eigenvector of min eigen value
#    and eigenvector of middle eigen value
# should now work if some eigenvalues are same as others
# these are the principal body axes
def evec(j,Ixx,Iyy,Izz,Ixy,Iyz,Ixz):
    Imat = np.matrix([[Ixx[j],Ixy[j],Ixz[j]],\
         [Ixy[j],Iyy[j],Iyz[j]],[Ixz[j],Iyz[j],Izz[j]]])
    w, v = LA.eig(Imat)  # eigenvecs v are unit length 
    jsort = np.argsort(w) # arguments of a sorted array of eigenvalues
    jmax = jsort[2]  # index of maximum eigenvalue
    jmin = jsort[0]  # index of minimum eigenvalue
    jmed = jsort[1]  # index of middle  eigenvalue
    vmax = np.squeeze(np.asarray(v[:,jmax]))   # corresponding eigenvector
    vmin = np.squeeze(np.asarray(v[:,jmin]))   # corresponding eigenvector
    vmed = np.squeeze(np.asarray(v[:,jmed]))   # corresponding eigenvector
    return vmax,vmin,vmed


# return eigenvalues!
# at index j
# order max,med,min
# these are I3,I2,I1 in order moments of inertia in body frame
def I3I2I1(j,Ixx,Iyy,Izz,Ixy,Iyz,Ixz):
    Imat = np.matrix([[Ixx[j],Ixy[j],Ixz[j]],\
         [Ixy[j],Iyy[j],Iyz[j]],[Ixz[j],Iyz[j],Izz[j]]])
    w, v = LA.eig(Imat)
    jsort = np.argsort(w) # arguments of a sorted array of eigenvalues
    jmax = jsort[2]  # index of maximum eigenvalue
    jmin = jsort[0]  # index of minimum eigenvalue
    jmed = jsort[1]  # index of middle  eigenvalue
    return w[jmax],w[jmed],w[jmin]


# to help give angles between 0 and pi/2
def piminus(ang):
    x = ang
    if (ang > np.pi/2.0):   # if angle greater than pi/2 returns pi-angle
        x = np.pi - ang
    return x

# body tilt angles with respect to body spin angular momentum and spin vectors
#   at index j 
# return acos of dot prod of spin omega with max principal axis
# return acos of dot prod of spin angular momentum with max principal axis
# and also returns same acosines for min and medium principal axis directions
def tilts(j,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz):
    slen = len_vec(omx[j],omy[j],omz[j])
    nox = omx[j]/slen;   # direction of omega (spin)
    noy = omy[j]/slen;
    noz = omz[j]/slen;
    llen = len_vec(llx[j],lly[j],llz[j])
    nlx = llx[j]/llen  # direction of spin angular momentum
    nly = lly[j]/llen
    nlz = llz[j]/llen
    vmax,vmin,vmed = evec(j,Ixx,Iyy,Izz,Ixy,Iyz,Ixz)  
    # evec returns eigenvectors of max and min and med eigenvalue of I matrix
    ds_ma =  dotprod(vmax[0],vmax[1],vmax[2],nox,noy,noz);  # cos = omega dot vmax
    dl_ma =  dotprod(vmax[0],vmax[1],vmax[2],nlx,nly,nlz);  # cos = angmom dot vmax
    # note that dl_ma is equivalent to cos J, 
    # with J the so-called non-principal rotation angle
    # see page 86 in Celletti's book
    ds_mi =  dotprod(vmin[0],vmin[1],vmin[2],nox,noy,noz);  # same but for vmin
    dl_mi =  dotprod(vmin[0],vmin[1],vmin[2],nlx,nly,nlz);  # "
    ds_me =  dotprod(vmed[0],vmed[1],vmed[2],nox,noy,noz);  # same but for vmed
    dl_me =  dotprod(vmed[0],vmed[1],vmed[2],nlx,nly,nlz);  # "
    angs_ma = piminus(np.arccos(ds_ma))    # return angles in range [0,pi/2]
    angl_ma = piminus(np.arccos(dl_ma))
    angs_mi = piminus(np.arccos(ds_mi))
    angl_mi = piminus(np.arccos(dl_mi))
    angs_me = piminus(np.arccos(ds_me))
    angl_me = piminus(np.arccos(dl_me))
    return angs_ma,angl_ma,angs_mi,angl_mi,angs_me,angl_me

# this angle is relevant for precession when spinning about a non-principal axis
# return the angle l conjugate to L (see page 86 of Celletti's book)
#   at array index j
# see Figure 5.2 by Celletti
def ll_vec(j,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz):
    vmax,vmin,vmed = evec(j,Ixx,Iyy,Izz,Ixy,Iyz,Ixz)  # body axis vectors
    llen = len_vec(llx[j],lly[j],llz[j])
    nlx = llx[j]/llen  # direction of spin angular momentum
    nly = lly[j]/llen
    nlz = llz[j]/llen
    # n_doublebar is vmax cross spin angular momentum direction nlx,nly,nlz
    ndd_x,ndd_y,ndd_z=crossprod_unit(vmax[0],vmax[1],vmax[2],nlx,nly,nlz)
    # we want vmin dotted with n_doublebar
    cosll =  dotprod(vmin[0],vmin[1],vmin[2],ndd_x,ndd_y,ndd_z); # vmin dot spin
    ang_ll = piminus(np.arccos(cosll))
    return ang_ll


# return averaged values for gdot and ldot
# these are Andoyer Deprit angles spin and precession rates
# using equations on page 88 of book by Celletti but averaging
# over possible values for l
# at index j
def body_precs(j,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz):
    I3,I2,I1 = I3I2I1(j,Ixx,Iyy,Izz,Ixy,Iyz,Ixz) 
    llen = len_vec(llx[j],lly[j],llz[j])
    G= llen   # spin angular momentum, and Andoyer Deprit variable
    nlx = llx[j]/llen  # direction of spin angular momentum
    nly = lly[j]/llen
    nlz = llz[j]/llen
    vmax,vmin,vmed = evec(j,Ixx,Iyy,Izz,Ixy,Iyz,Ixz)  
    # evec returns eigenvectors of max and min and med eigenvalue of I matrix
    cosJ =  dotprod(vmax[0],vmax[1],vmax[2],nlx,nly,nlz);  # cos = angmom dot vmax
    # J is the so-called non-principal rotation angle
    # see page 86 in Celletti's book
    L = np.abs(G*cosJ) # Andoyer Deprit variable
    inv_I_med = 0.5*(1.0/I1 + 1.0/I2);
    gdot =G*inv_I_med  # averaged over l page 88 Celletti
    ldot = L/I3 - L*inv_I_med # averaged over l 
    lambda1dot = L/I3 + G*inv_I_med - L*inv_I_med  # is gdot + ldot
    return gdot,ldot,lambda1dot


# vector of tilts
# do it for every k spacing in index, not every index (unless k=1)
# returns angles for largest eigendirection of I and minimum and medium
# returns angles for both omega and spin angular momentum 
# the angles are those between omega and eigendirections
#  or those between spin and eigendirections
# the eigendirections are the principal axes
def vec_tilts(k,tt,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz):
    nn = np.size(tt)
    nt = np.int(nn/k)
    svec_ma=[]
    lvec_ma=[]
    svec_mi=[]
    lvec_mi=[]
    svec_me=[]
    lvec_me=[]
    tvec=[]
    ang_ll_vec = []
    gdot_vec =[]
    ldot_vec =[]
    lam1dot_vec = []
    omvec = np.sqrt(omx*omx + omy*omy + omz*omz)
    Gvec = np.sqrt(llx*llx + lly*lly + llz*llz)
    spin_vec = []
    for i in range(nt):
        j = k*i
        angs_ma,angl_ma,angs_mi,angl_mi,angs_me,angl_me =\
              tilts(j,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz) 
        svec_ma = np.append(svec_ma,angs_ma)  #largest
        lvec_ma = np.append(lvec_ma,angl_ma)
        svec_mi = np.append(svec_mi,angs_mi)  #smallest
        lvec_mi = np.append(lvec_mi,angl_mi)
        svec_me = np.append(svec_me,angs_me)  #medium
        lvec_me = np.append(lvec_me,angl_me)
        spin_vec = np.append(spin_vec,omvec[j])
        tvec = np.append(tvec,tt[j])  #time
        ang_ll = ll_vec(j,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz) 
        ang_ll_vec = np.append(ang_ll_vec,ang_ll)
        gdot,ldot,lam1dot = body_precs(j,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz) 
        gdot_vec=np.append(gdot_vec,gdot)
        ldot_vec=np.append(ldot_vec,ldot)
        lam1dot_vec=np.append(lam1dot_vec,lam1dot)

    return tvec,svec_ma,lvec_ma,svec_mi,lvec_mi,svec_me,lvec_me,ang_ll_vec,gdot_vec,ldot_vec,lam1dot_vec,spin_vec



# compute orbital elements for com of resolved and first mass w.r.t to another mass
def orbel_com(fileroot,numberpm,ip):
    t,x,y,z,vx,vy,vz,omx,omy,omz,llx,lly,llz,Ixx,Iyy,Izz,Ixy,Iyz,Ixz,KErot,PEspr,PEgrav,Etot,dEdt=\
       readresfile(fileroot)  # resolved body stuff
    tt, mvec, xarr,yarr,zarr,vxarr,vyarr,vzarr=\
       readallpmfiles(fileroot,numberpm)  # point mass stuff
    m0 = 1.0
    m1 = mvec[0]
    M = m0+m1
    imc = 0 
    x0 = (m0*x + m1*np.squeeze(xarr[imc]))/M   # COM coordinate  for resolved and central mass imc
    y0 = (m0*y + m1*np.squeeze(yarr[imc]))/M    
    z0 = (m0*z + m1*np.squeeze(zarr[imc]))/M    
    vx0 = (m0*vx + m1*np.squeeze(vxarr[imc]))/M  
    vy0 = (m0*vy + m1*np.squeeze(vyarr[imc]))/M  
    vz0 = (m0*vz + m1*np.squeeze(vzarr[imc]))/M  
 
    dxarr = x0-np.squeeze( xarr[ip]);  dyarr= y0-np.squeeze( yarr[ip]);  dzarr= z0-np.squeeze( zarr[ip]);
    dvxarr=vx0-np.squeeze(vxarr[ip]); dvyarr=vy0-np.squeeze(vyarr[ip]); dvzarr=vz0-np.squeeze(vzarr[ip]);

    nl = len(tt)
    kk = np.int(nl/plmax)    # reduce array sizes by this interval!
    if (kk<1): 
        kk=1

    ts = t[0::kk]  # short time array
    dxarr   = dxarr[0::kk];  dyarr =  dyarr[0::kk];  dzarr =  dzarr[0::kk]
    dvxarr = dvxarr[0::kk]; dvyarr = dvyarr[0::kk]; dvzarr = dvzarr[0::kk]
    aaarr_p = dxarr*0.0; eearr_p = dxarr*0.0; iiarr_p = dxarr*0.0;
    lnarr_p = dxarr*0.0; ararr_p = dxarr*0.0; maarr_p = dxarr*0.0;
    for k in range(len(dxarr)):
        aa,ee,ii,longnode,argperi,meananom=\
               keplerian(M +mvec[ip],dxarr[k],dyarr[k],dzarr[k],dvxarr[k],dvyarr[k],dvzarr[k])
        aaarr_p[k] = aa
        eearr_p[k] = ee
        iiarr_p[k] = ii
        lnarr_p[k] = longnode
        ararr_p[k] = argperi 
        maarr_p[k] = meananom 
    return ts,aaarr_p,eearr_p,iiarr_p,lnarr_p,ararr_p,maarr_p


