# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT 
# WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
# MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

##################################################
# This program implements the first LP introduced#
# in Image reconstruction by linear programming  #
# by Tsuda et al IEEE Transactions on Image      #
# Processing, vol. 14, no. 6, pp. 737-744, June  #
# 2005, doi: 10.1109/TIP.2005.846029             #
#                                                #
# A set of basis PNG images is read in, along    #
# with a specified noisy image, and the denoised #
# image is written to a PNG                      #
##################################################
# some small change                              #

from PIL import Image
import numpy as np
import os
from csv import writer
from scipy.optimize import linprog

directory = "../Basis Images"
noisyimagefile ="../NoisyImage.png"
outputimagefile ="../DenoisedImage.png"
nu = 0.1 #tunable regularizer: approx = % of noisy pixels

#print(os.listdir(directory)[0])


##################################################
########## 1. count the number of files ##########
##################################################
nfiles = 0
for filename in os.listdir(directory):
    nfiles +=1
    #print(filename)

print(nfiles," files found in ",directory)


##################################################
########## 2. get dimensions of images  ##########
##################################################
firstImage = Image.open(directory+'/'+os.listdir(directory)[0])
firstImageSize = firstImage.size
(width,height)=firstImageSize
N=width*height
print(N)
print("Dimensions of first image are ",firstImage.size)


##################################################
########## 3. create data Matrix        ##########
##################################################
dataMatrix = [];
j=0
for filename in os.listdir(directory):
    #open j-th image, check if they're correct size
    im = Image.open(directory+'/'+os.listdir(directory)[j])
    if im.size != firstImageSize:
        print('image ',filename, ' has wrong size:', im.size)
    j +=1

    #convert Image to grayscale
    im=im.convert('L')

    #transform into numpy array and add to B
    gsarray = (np.array(im)).flatten()
    dataMatrix.append(gsarray)

Braw=np.asarray(dataMatrix)
B=Braw.astype(float)
print(B)


##################################################
########## 4. save B to CSV             ##########
##################################################
if os.path.exists("B.csv"):
    os.remove("B.csv")
with open('B.csv', 'a', newline='') as f_object:
    writer_object = writer(f_object)
    for i in range(nfiles):
        writer_object.writerow(B[i])
        
    f_object.close()

##################################################
########## 5. create W matrix           ##########
##################################################
W = np.zeros(shape=(N,2*N))
print(W)

k=0
for i in range(N):
    W[i,k]=1
    W[i,k+1]=-1
    k+=2

print(W)


##################################################
########## 6. write W to csv            ##########
##################################################
if os.path.exists("W.csv"):
    os.remove("W.csv")
with open('W.csv', 'a', newline='') as f_object:
    writer_object = writer(f_object)
    for i in range(N):
        writer_object.writerow(W[i])
        
    f_object.close()


##################################################
########## 7. create A matrix           ##########
##################################################   
epsilon = np.ones((N,1))
print(epsilon)
A = np.zeros(shape=(2*N,2*N+nfiles+1))
A = np.block([[W,-np.transpose(B),-epsilon],[-W,np.transpose(B),-epsilon]])

print(type(W))
print(type(B))
print(A)

##################################################
########## 8. write A to csv            ##########
##################################################
if os.path.exists("A.csv"):
    os.remove("A.csv")
with open('A.csv', 'a', newline='') as f_object:
    writer_object = writer(f_object)
    for i in range(2*N):
        writer_object.writerow(A[i])
        
    f_object.close()

print(type(B[0,0]))


##################################################
########## 10. import noisy image       ##########
##################################################
noisyImage = Image.open(noisyimagefile)
noisyImage = noisyImage.convert('L')
noisyImageArray = np.array(im).flatten()
b=[]
for i in range(N):
    b.append(-noisyImageArray[i].astype(float))
for i in range(N):
    b.append(noisyImageArray[i].astype(float))

print(noisyImageArray)
print(b)


##################################################
########## 11. write cost vector        ##########
##################################################
c = []
nu = nu
for i in range(2*N+nfiles+1):
    if i<2*N:
        c.append(1/N)
    elif i>=2*N and i<2*N+nfiles:
        c.append(0)
    elif i>=2*N+nfiles:
        c.append(nu)
print(c)


##################################################
########## 12. solve LP                 ##########
##################################################
res = linprog(c,A_ub=A, b_ub=b,options={"maxiter":10})
print(res.x)
x=res.x

        
##################################################
########## 13. generate image from denoised data #
##################################################

#construct xbar: xbar = alphaplus - alphaminus + x
xbar = []
for i in range(N):
    xbar.append(x[2*i]-x[2*i+1]+noisyImageArray[i])
print(xbar)

denoisedImageData = np.zeros((width,height))

for i in range(width):
    for j in range(height):
        denoisedImageData[i,j]=xbar[width*i+j]      
print(denoisedImageData)

denoisedImage = Image.fromarray(denoisedImageData)
denoisedImage = denoisedImage.convert('RGB')
denoisedImage.save(outputimagefile,format="PNG")

print("program complete")