# Calculating SVD for CLM output
# 10/18/18

#source /glade/work/kdagon/ncar_pylib_clone/bin/activate

import numpy as np
from scipy.io import netcdf as nc
import matplotlib.pyplot as plt

# Select output variable
#var = "GPP"
var="LHF"

# Get landfrac from an existing PPE simulation (constant throughout simulations)
f_lf = nc.netcdf_file("/glade/scratch/kdagon/archive/hydro_ensemble_LHC_1/lnd/hist/hydro_ensemble_LHC_1.clm2.h0.0016-01.nc",'r',mmap=False)
lf = f_lf.variables['landfrac']
landfrac = lf[:]

# Mask landfrac to account for netcdf FillValues (a bit hacky)
import numpy.ma as ma
landfrac_mask = ma.masked_where(landfrac > 1e34, landfrac) # sufficiently large to mask FillValues (~1e36)

# Read netcdf file (pre-processed in NCL)
f = nc.netcdf_file("../outputdata/outputdata_"+var+"_forSVD_100.nc",'r',mmap=False)
#f = nc.netcdf_file("outputdata/outputdata_"+var+"_forSVD_100_v2.nc",'r',mmap=False)
#f = nc.netcdf_file("outputdata/outputdata_"+var+"_forSVD_100_fc.nc",'r',mmap=False)
#f = nc.netcdf_file("outputdata/outputdata_"+var+"_forSVD_100_diff.nc",'r',mmap=False)
#f = nc.netcdf_file("outputdata/outputdata_"+var+"_forSVD_100_WECANNmask.nc",'r',mmap=False)

# Read variable data
X = f.variables[var]
mask = f.variables['datamask']

# Convert to numpy array
d = X[:]
#plt.contourf(d[0,:,:])
#plt.colorbar()
#plt.show()
m = mask[:]

# Get dimensions
# the order here is important
nens=d.shape[0]
nlat=d.shape[1]
nlon=d.shape[2]

# Mask landfrac (again!) to match obs mask
landfrac_mask_obs = ma.masked_where(m==0, landfrac_mask)

# Reshape so input is (..,M,N) which is important for svd 
#dr = np.reshape(d,(nens,nlat*nlon))
#print(dr.shape)
#mr = np.reshape(m,nlat*nlon)

# Replace masked gridpoints with zero (shouldn't impact SVD?)
#dr[:,mr==0] = 0
# Replace FillValue with zero (shouldn't impact SVD?)
#dr[dr==1.e+36] = 0

# Alternate: subset dr for land only grid points
#drm = dr[:,mr==1]
#print(drm.shape)
# Still need to get rid of lingering FillValues (why do they not match the mask?)
# likely need this step because FLUXNET mask is based on first month only
#drm[drm==1.e+36] = 0
# Test plot
#plt.contourf(drm)
#plt.colorbar()
#plt.show()

# Subset using final landfrac mask
i,j = np.nonzero(landfrac_mask_obs)
dr = d[:,i,j]

# SVD command (no trunc option)
#U,s,Vh = np.linalg.svd(drm, full_matrices=False)
U,s,Vh = np.linalg.svd(dr, full_matrices=False)  
#print(U.shape)
#print(U[:,0]) # first mode
#plt.hist(U[:,0], bins=20)
#plt.show()
#print(s.shape)
#print(s) # singular values
prop_var = s**2/np.sum(s**2)
#print(prop_var) # proportion of variance explained
print(np.sum(prop_var)) # should be 100%
print(np.sum(prop_var[0:3])) # first 3 modes, total variance
print(prop_var[0:3]) # first 3 modes, individual variance
var_modes = prop_var[0:3]
#print(Vh.shape)
# Columns of U are modes of variability
# And the rows are ensemble members
# Singular values are in s

# Sanity check - reconstruction
print(np.allclose(dr, np.dot(U*s, Vh)))
smat = np.diag(s)
print(np.allclose(dr, np.dot(U, np.dot(smat, Vh))))

# need to increase tolerance for LHF (doesn't close otherwise)
#print(np.allclose(drm, np.dot(U*s, Vh), atol=1e-07))
#print(np.allclose(drm, np.dot(U, np.dot(smat, Vh)), atol=1e-06))
#print(drm[:,0]-np.dot(U*s, Vh)[:,0])

# Plot first mode of model U-vector (distribution)
#plt.hist(U[:,0], bins=20)
#plt.xlabel('Mode 1 of '+var+' SVD (U-vector)')
#plt.ylabel('Counts')
#plt.savefig("dist_outputdata_GPP_SVD_mode1.pdf")
#plt.savefig("dist_outputdata_LHF_SVD_mode1.pdf")
#plt.savefig("dist_outputdata_diff_"+var+"_SVD_mode1.pdf")
#plt.show()

# Save out first n modes from SVD
# Note: cannot save masked array to file (this way)
# Full SVD
#np.save("outputdata/outputdata_GPP_SVD_3modes", U[:,0:3])
#np.save("outputdata/outputdata_LHF_SVD_3modes", U[:,0:3])
#np.save("outputdata/outputdata_GPP_SVD_3modes_v2", U[:,0:3])
#np.save("outputdata/outputdata_LHF_SVD_3modes_v2", U[:,0:3])
#np.save("outputdata/outputdata_GPP_SVD_3modes_fc", U[:,0:3])
#np.save("outputdata/outputdata_LHF_SVD_3modes_fc", U[:,0:3])
#np.save("outputdata/outputdata_GPP_SVD_3modes_diff", U[:,0:3])
#np.save("outputdata/outputdata_LHF_SVD_3modes_diff", U[:,0:3])

# Exit script before obs
#import sys
#sys.exit()

# Compare with Observations

# Read netcdf file (pre-processed in NCL)
# anomalies from ensemble mean where ensemble does not include obs (n=100)
fo = nc.netcdf_file("../obs/obs_"+var+"_4x5_anom_forSVD.nc",'r',mmap=False)
#fo = nc.netcdf_file("obs/WECANN_"+var+"_4x5_anom_forSVD.nc",'r',mmap=False)

# Read variable data
Xo = fo.variables[var]
masko = fo.variables['datamask']

# Convert to numpy array
do = Xo[:]
#print(do.shape)
mo = masko[:]
#print(mo.shape)

# Get dims
nenso=1
nlato=do.shape[0]
nlono=do.shape[1]

# Reshape so input is (..,M,N) which is important svd 
# Where M=nenso, N=ngrid=nlato*nlono
#dro = np.reshape(do,(nenso,nlato*nlono))
#print(dro.shape)
#mro = np.reshape(mo,nlato*nlono)
#print(mro.shape)

# Replace masked gridpoints with zero (shouldn't impact SVD?)
#do[mo==0] = 0
# Replace FillValue with zero (shouldn't impact SVD?)
#do[do==-9999] = 0

# Alternate: subset do for land only grid points
#drom = dro[:,mro==1]
#print(drom.shape)
# If FillValues persist...
#drom[drom==-9999] = 0
# Test plot
#plt.plot(drom[0,:])
#plt.show()

# Subset using final landfrac mask
#i,j = np.nonzero(landfrac_mask_obs)
dom = do[i,j]

# Project obs into SVD space
from numpy.linalg import pinv
U_obs = np.dot(dom,pinv(np.dot(smat,Vh)))
#print(U_obs.shape)
#print(U_obs)

# Print out U_obs for first mode
#print(U_obs[:,0])
# First 3 modes
#print(U_obs[:3])

# Save out first n modes of U_obs
#np.save("obs/obs_"+var+"_SVD_3modes", U_obs[:,0:3])
#np.save("obs/WECANN_"+var+"_SVD_3modes", U_obs[:,0:3]) 

# Plot first mode of model U-vector (distribution) with U_obs (vertical line)
#plt.hist(U[:,0], bins=20)
#plt.xlabel('Mode 1 of '+var+' SVD (U-vector)')
#plt.ylabel('Counts')
#plt.axvline(x=U_obs[0], color='r', linestyle='dashed', linewidth=2)
#plt.savefig("dist_outputdata_"+var+"_SVD_mode1_withobs.pdf")
#plt.savefig("dist_outputdata_"+var+"_SVD_mode1_withWECANN.pdf")
#plt.show()

# Project test paramset into SVD space
testset = "v5"

#ft = nc.netcdf_file("outputdata/test_paramset_SVD_006_GPP_forSVD.nc",'r',mmap=False)
#ft = nc.netcdf_file("outputdata/test_paramset_SVD_006_LHF_forSVD.nc",'r',mmap=False)
#ft = nc.netcdf_file("outputdata/test_paramset_LHF_SVD_001_forSVD.nc",'r',mmap=False)
#ft = nc.netcdf_file("outputdata/test_paramset_"+var+"_forSVD.nc",'r',mmap=False)
ft = nc.netcdf_file("../outputdata/test_paramset_"+testset+"_"+var+"_forSVD.nc",'r',mmap=False)

Xt = ft.variables[var]
maskt = ft.variables['datamask']
dt = Xt[:]
mt = maskt[:]
dtm = dt[i,j]
#drt = np.reshape(dt,(nenso,nlato*nlono))
#mrt = np.reshape(mt,nlato*nlono)
#drtm = drt[:,mrt==1]
#print(drtm.shape)
#drtm[drtm==1.e+36] = 0
U_test = np.dot(dtm,pinv(np.dot(smat,Vh)))
print("Simulated "+var+" modes = ",U_test[:3])
# Calculate likelihood based on these results
#sd = np.load(file="obs/obs_"+var+"_SVD_3modes_allyrs_sd.npy")
#L = np.sum(var_modes*((U_test[:3]-U_obs[:3])/sd)**2)
# weighted L (LHF)
#B = 1.3
#B = 1.49
#L = B*np.sum(((U_test[:,0:3]-U_obs[:,0:3])/sd)**2, axis=1)
#print(L)

# Plot distribution with U_obs and U_test
#plt.hist(U[:,0], bins=20)
#plt.xlabel('Mode 1 of GPP SVD (U-vector)')
#plt.ylabel('Counts')
#plt.axvline(x=U_obs[0], color='r', linestyle='dashed', linewidth=2)
#plt.axvline(x=U_test[0], color='b', linestyle='dashed', linewidth=2)
#plt.show()

# Project model with default params into SVD space
fd= nc.netcdf_file("../outputdata/CLM_default_"+var+"_forSVD.nc",'r',mmap=False)
#fd=nc.netcdf_file("outputdata/CLM_default_"+var+"_forSVD_WECANNmask.nc",'r',mmap=False)
Xd = fd.variables[var]
maskd = fd.variables['datamask']
dd = Xd[:]
md = maskd[:]
ddm = dd[i,j]
#drd = np.reshape(dd,(nenso,nlato*nlono))
#mrd = np.reshape(md,nlato*nlono)
#drdm = drd[:,mrd==1]
#print(drdm.shape)
#plt.plot(drdm[0,:])
#plt.show()
# if FillValues persist...
#drdm[drdm==1.e+36] = 0
U_default = np.dot(ddm,pinv(np.dot(smat,Vh)))
#print(U_default[:3])

# Save out first n modes of U_default
#np.save("outputdata/modeldefault_GPP_SVD_3modes", U_default[:,0:3])
#np.save("outputdata/modeldefault_LHF_SVD_3modes", U_default[:,0:3])

# Plot distribution with U_default
plt.hist(U[:,0], bins=20)
plt.xlabel('Mode 1 of '+var+' SVD (U-vector)')
plt.ylabel('Counts')
plt.axvline(x=U_obs[0], color='r', linestyle='dashed', linewidth=2)
plt.axvline(x=U_test[0], color='b', linestyle='dashed', linewidth=2)
plt.axvline(x=U_default[0], color='k', linestyle='dashed', linewidth=2)
#plt.savefig("dist_outputdata_"+var+"_SVD_mode1_withobs_anddefault.pdf")
#plt.savefig("dist_outputdata_"+var+"_SVD_mode1_withWECANN_anddefault.pdf")      
plt.show()

# Second mode
plt.hist(U[:,1], bins=20)
plt.xlabel('Mode 2 of '+var+' SVD (U-vector)')
plt.ylabel('Counts')
plt.axvline(x=U_obs[1], color='r', linestyle='dashed', linewidth=2)
plt.axvline(x=U_test[1], color='b', linestyle='dashed', linewidth=2)
plt.axvline(x=U_default[1], color='k', linestyle='dashed', linewidth=2)
#plt.savefig("dist_outputdata_"+var+"_SVD_mode2_withobs_anddefault.pdf")
#plt.savefig("dist_outputdata_"+var+"_SVD_mode2_withWECANN_anddefault.pdf")  
plt.show()

# Third mode
plt.hist(U[:,2], bins=20)
plt.xlabel('Mode 3 of '+var+' SVD (U-vector)')
plt.ylabel('Counts')
plt.axvline(x=U_obs[2], color='r', linestyle='dashed', linewidth=2)
plt.axvline(x=U_test[2], color='b', linestyle='dashed', linewidth=2)
plt.axvline(x=U_default[2], color='k', linestyle='dashed', linewidth=2)    
#plt.savefig("dist_outputdata_"+var+"_SVD_mode3_withobs_anddefault.pdf")
#plt.savefig("dist_outputdata_"+var+"_SVD_mode3_withWECANN_anddefault.pdf")   
plt.show()
