# LPFParser.py
# Author: Lucas Hartsough
#         lucash@rice.edu
# Description: Package of helper functions for parsing and plotting LPF files.
# Requires: numpy, matplotlib (for plotting; optional)

# --------------------------------
## Import packages ##
# --------------------------------
try:
    import numpy as np
    import struct

    def trueIndex(positions, randMat):
        '''Returns the plate index of the wells with the given (pre-randomized) indices.'''
        returnInt = False
        if type(positions) is int:
            positions = np.array([positions])
            returnInt = True
        elif type(positions) is list:
            positions = np.array(positions)
        elif type(positions) is not np.ndarray:
            raise IOError("Positions parameter must be a list or an integer.")
        if type(randMat) is not list and type(randMat) is not np.ndarray:
            raise IOError("randMat parameter must be a list.")
        for i in randMat:
            if type(i) is not int:
                raise IOError("All elements in randMat must be integers")
        truePositions = []
        for i in positions:
            try:
                truePositions.append(randMat[i])
            except IndexError:
                raise IndexError("All positions must be integers and smaller than the length of randMat.")
        if returnInt:
            return truePositions[0]
        else:
            return truePositions

    def LPFtoArray(LPFfile, rowNum=4, colNum=6, channelNum=2, verbose=True):
        '''Returns a dict with parsed LPF data.
        Inputs:
        LPFfile (str/File Obj) -- relative path to LPF file to be parsed, either as a str or the File Obj variable
            Note: the LPF is automatically closed at the end.
        rowNum (int) -- number of rows in the device [default: 4]
        colNum (int) -- number of cols in the device [default: 6]
        channelNum (int) -- number of channels in the device [default: 2]
        verbose (bool) -- whether to print header information during parsing
        Returns: dict with keys:
            'header': list of raw header data
            'data': tuple of:
                [0]: array of time points (ms) corresponding to the time steps in the LPF data
                [1]: 4D numpy array with LPF data: [times][rows][cols][channels]
        '''
        output = {}
        if type(LPFfile) == str:
            LPFfile = open(LPFfile, 'rb')
        header = struct.unpack('I'*8, LPFfile.read(32))
        output['header'] = header
        if verbose:
            print("Header:\n\t%s"%repr(header))
        numPts = header[3]
        timeStep = header[2]
        if verbose:
            print("Header Data:")
            print("\tLPF ver: %d"%header[0])
            print("\tNumber of channels (total): %d"%header[1])
            print("\tTime step: %d (ms)"%timeStep)
            print("\tNumber of time steps: %d"%numPts)
        if header[1] != rowNum * colNum * channelNum:
            raise IOError("Product of rowNum, colNum, & channelNum (%d) != total channels in the LPF (%d)"%(rowNum*colNum*channelNum, header[1]))
        times = np.arange(0, numPts*timeStep, timeStep)
        ints = np.zeros((header[3], rowNum, colNum, channelNum))
        for tp in range(numPts):
            for r in range(rowNum):
                for c in range(colNum):
                    for ch in range(channelNum):
                        ints[tp,r,c,ch] = int(struct.unpack('h', LPFfile.read(2))[0])
        LPFfile.close()
        if verbose:
            print("Intensity Data:")
            print("\tParsed %d time points (%.2fmin)"%(len(times), times[-1]/1000./60.))
        output['data'] = (times, ints)
        return output

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("matplotlib is required for plotting. Please install it using 'pip install matplotlib'.")



    def plotLPFData(data, channels, wellIndices, rowNum, colNum, savePath, mplargs):
        """
        Function to plot LPF data.

        Arguments:
        - data: The LPF data to be plotted, likely a multi-dimensional numpy array.
        - channels: List of channel indices (e.g., [0,1]).
        - wellIndices: List of well indices provided as input.
        - rowNum: Number of rows in the grid.
        - colNum: Number of columns in the grid.
        - savePath: Path to save the resulting plot.
        - mplargs: Dictionary of matplotlib arguments, e.g., line width (lw), alpha (transparency), etc.
        """
        import matplotlib.pyplot as plt

        # Step 1: Validate rcIndices
        try:
            # Generate indices based on rowNum (rows) and colNum (columns)
            rcIndices = [(well // colNum, well % colNum) for well in wellIndices]
        except Exception as e:
            raise ValueError(f"Error while calculating rcIndices: {e}\nCheck wellIndices, rowNum, and colNum.")

        first = True

        # Step 2: Plot the LPF data
        try:
            for welli in range(len(rcIndices)):
                for chi in channels:
                    # Validate rcIndices[welli]
                    if not isinstance(rcIndices[welli], (tuple, list)) or len(rcIndices[welli]) != 2:
                        raise ValueError(
                            f"Invalid rcIndices[welli]: {rcIndices[welli]}. Expected a tuple/list of length 2."
                        )

                    # Unpack row and column indices
                    r, c = rcIndices[welli]

                    # First plot initialization
                    if first:
                        plt.step(
                            data[0] / 1000. / 60.,  # X-axis data
                            data[1][:, r, c, chi],  # Y-axis data
                            lw=mplargs['lw'],
                            alpha=mplargs['alpha'],
                            label=f"Ch{chi} R{r}C{c}"
                        )
                        first = False
                    else:
                        plt.step(
                            data[0] / 1000. / 60.,
                            data[1][:, r, c, chi],
                            lw=mplargs['lw'],
                            alpha=mplargs['alpha']
                        )

            # Configure plot and save
            plt.xlabel('Time (hours)')
            plt.ylabel('Signal Intensity')
            plt.legend()
            plt.savefig(savePath)
            plt.close()

        except IndexError as e:
            raise IndexError(
                f"IndexError while plotting data: {e}\nCheck the dimensions and indices of the input data.")
        except Exception as e:
            raise RuntimeError(f"An error occurred during plotting: {e}")


        def wellIndextoRC(index, colNum, rowNum=None):
            '''Returns the row and column index of a given well index.'''
            return (index/colNum, index%colNum)

        rcIndices = [] # List of row and column indices for the selected wellIndices
        for i in wellIndices:
            rcIndices.append(wellIndextoRC(i, colNum))

        plt.figure(figsize=(8,6), dpi=150)
        first = True # only the first set gets legend labels
        for welli in range(len(rcIndices)):
            for chi in channels:
                r,c = rcIndices[welli]
                if first:
                    plt.step(data[0]/1000./60., data[1][:,r,c,chi], lw=mplargs['lw'], alpha=mplargs['alpha'],
                             color=mplargs['chColors'][chi], label=mplargs['chLabels'][chi], where='post')
                else:
                    plt.step(data[0]/1000./60., data[1][:,r,c,chi], lw=mplargs['lw'], alpha=mplargs['alpha'],
                             color=mplargs['chColors'][chi], where='post')
            first = False
        if mplargs['title'] != '':
            plt.title(mplargs['title'], fontsize=mplargs['title_size'], fontweight=mplargs['fontweight'])
        plt.xlabel(mplargs['xlabel'], fontsize=mplargs['xlabel_size'], fontweight=mplargs['fontweight'])
        plt.ylabel(mplargs['ylabel'], fontsize=mplargs['ylabel_size'], fontweight=mplargs['fontweight'])
        plt.xticks(fontsize=mplargs['ticklabel_size'], fontweight=mplargs['fontweight'])
        plt.yticks(fontsize=mplargs['ticklabel_size'], fontweight=mplargs['fontweight'])
        if mplargs['xlim'] is not None:
            plt.xlim(mplargs['xlim'])
        else:
            xlimlow = 0 - 0.05*data[0][-1]/1000./60. # 5% of the total time left of 0
            xlimhigh = 1.05*data[0][-1]/1000./60. # 5% of the total time right of max
            plt.xlim((xlimlow, xlimhigh))
        if mplargs['ylim'] is not None:
            plt.ylim(mplargs['ylim'])
        else:
            plt.ylim((-800,4100))
        if mplargs['legend_loc'] is not None:
            plt.legend(loc=mplargs['legend_loc'])
        if savePath is not None:
            if type(savePath) is not str:
                raise TypeError("savePath must be a string")
            plt.savefig(savePath, dpi=150, bbox_inches='tight')

except ImportError:
    print("Plotting functions disabled; matplotlib not found.")
