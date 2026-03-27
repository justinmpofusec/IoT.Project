#The code for the graph

# This is import section of the code. This allows you import of the libary of code which is not available with vanilla python

import datetime # Allows numbers to be formatted into date and times
import matplotlib.pyplot as plt  # Allows graphs to be made from data
import matplotlib.animation as animation #Allows the graph be autoupdateed
from matplotlib import style # Makes the graph look nicer
style.use('fivethirtyeight')


# The initalisation of the graph. Subplots are created
fig = plt.figure()
ax1 = fig.add_subplot(2,2,1) # (Number of column, number of rows, order)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)
ax4 = fig.add_subplot(2,2,4)

# This is animate function. This function will be on loop untill the graph is closed. First it will open Connections.csv; then it will check on the connections to the server.
# It will then go through each the connections, trying to open its unique sensor data file. If there is one it will open it. Then it will go through the sensor data and add the data into it's correspodning arrays
# Using the array that are now filled with senor data it will plot the data onto the graphs. Then the graph is shown to the user.
# This process will be done for each connection
def animate(i):

    f=open("Connections.csv","r")
    rows=f.readlines()
    f.close()

    # This clears the graphs
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()

    # This will make sure all the connections get thier sensor data shown
    for column in rows:
        column=column.split(",")
        column[1]=column[1].strip()

        # Intial arrays where sensor data is shown aganist time when the senor data was taken
        xVal1 = []
        yT1 = []
        yM1 = []
        yH1 = []
        yP1 = []

        try:
            graphData=open("TempData "+ str(column[1])+".csv","r")
            graphDataR=graphData.readlines()
            for elem in graphDataR[1:]:
                elemS=elem.split(",")
                datetimeVar=datetime.datetime.strptime(str(elemS[0])+" "+str(elemS[1])+" "+str(elemS[2])+" "+str(elemS[3]),"%Y-%m-%d %H %M %S")
                xVal1.append(datetimeVar)
                yT1.append(float(elemS[5]))
                yP1.append(float(elemS[6])*100)
                yH1.append(float(elemS[7]))
                yM1.append(float(elemS[14]))

            fig.suptitle("Environmental Data")

            ax1.set_ylabel("Temperature (Degrees c)")
            ax1.set_xlabel("Time")
            ax1.plot(xVal1,yT1,label="Device "+str(column[0]))
            ax1.legend(loc= "upper right")

            ax2.set_ylabel("% Relative Moisture")
            ax2.set_xlabel("Time")
            ax2.plot(xVal1,yH1,label="Device "+str(column[0]))
            ax2.legend(loc= "upper right")

            #ax3.ticklabel_format(useOffset=False)
            ax3.set_ylabel("Pressure (Pascals Pa)")
            ax3.set_xlabel("Time")
            ax3.plot(xVal1,yP1,label="Device "+str(column[0]))
            ax3.legend(loc= "upper right")

            ax4.set_ylabel("Magnetic Flux Densisity (Teslas)")
            ax4.set_xlabel("Time")
            ax4.plot(xVal1,yM1,label="Device "+str(column[0]))
            ax4.legend(loc= "upper right")

        except FileNotFoundError as fnf_error:
            print(fnf_error)

def main():
    ani=animation.FuncAnimation(fig,animate,interval = 1000) # This where the animation of the graph are started.
    plt.show()# The graph is shown

# This find whether the code is being run from its source or from another python file. If its the former then this program will run.
if __name__ == '__main__':
    main()
