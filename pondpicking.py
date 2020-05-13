class PondPicker:
    def __init__(self, pond):
        'get pond data and initialize plot'
        
        # get pond data from Open Altimetry
        import numpy as np
        import matplotlib.pylab as plt
        import json
        import requests
        self.pond = pond
        if pond == 1:
            self.latlims = [-72.9969, -72.9890]
            self.lonlims = [67.2559, 67.2597]
            self.hlims = [217, 224]
            #self.has2parts = True
        elif pond == 2: 
            self.latlims = [-72.8937, -72.8757]
            self.lonlims = [67.3046, 67.3131]
            self.hlims = [204, 212]
            #self.has2parts = True
        elif pond == 3: 
            self.latlims = [-71.8767, -71.8669]
            self.lonlims = [67.7598, 67.7640]
            self.hlims = [89, 98]
            #self.has2parts = True
        elif pond == 4: 
            self.latlims = [-71.6481, -71.6376]
            self.lonlims = [67.8563, 67.8608]
            self.hlims = [76, 88]
            #self.has2parts = False
        self.url = 'https://openaltimetry.org/data/api/icesat2/atl03?minx={minx}&miny={miny}&maxx={maxx}&maxy={maxy}&trackId=81&beamName=gt2l&outputFormat=json&date=2019-01-02&client=jupyter'
        self.url = self.url.format(minx=self.lonlims[0],miny=self.latlims[0],maxx=self.lonlims[1],maxy=self.latlims[1])
        print('requesting data: ', self.url)
        self.conf_ph = ['Buffer', 'Low', 'Medium', 'High']
        r = requests.get(self.url)
        self.data = r.json()
        self.lat_ph = []
        self.lon_ph = []
        self.h_ph = []
        for beam in self.data:
            for photons in beam['series']:
                if any(word in photons['name'] for word in self.conf_ph):
                    for p in photons['data']:
                        self.lat_ph.append(p[0])
                        self.lon_ph.append(p[1])
                        self.h_ph.append(p[2])
        
        # plot the data 
        self.fig = plt.figure(figsize=[9, 6.5])
        self.ax = self.fig.add_subplot(111)
        self.colph = np.array([[0.25, 0.25, 0.25]])
        self.cols = 'b'
        self.colb = np.array([252, 3, 73]) / 255
        self.ax.set_title("EDITING THE POND SURFACE: click to select points\npress '2' to edit the lake bed\npress 'backspace' to delete last point or 'n' to start a new line segment",color=self.cols)
        self.ax.set_xlabel('latitude')
        self.ax.set_ylabel('elevation [m]')
        self.ax.spines['bottom'].set_color(self.cols)
        self.ax.spines['left'].set_color(self.cols)
        self.ax.spines['top'].set_color(self.cols)
        self.ax.spines['right'].set_color(self.cols)
        self.ax.xaxis.label.set_color(self.cols)
        self.ax.yaxis.label.set_color(self.cols)
        self.ax.tick_params(axis='x', colors=self.cols)
        self.ax.tick_params(axis='y', colors=self.cols)
        self.phscat = self.ax.scatter(self.lat_ph,self.h_ph,s=30,c=self.colph,alpha=0.2,edgecolors='none')
        self.sline, = self.ax.plot([],[],c=self.cols,ls='-',marker='o',ms=3,mfc='w',mec=self.cols)
        self.bline, = self.ax.plot([],[],c=self.colb,ls='-',marker='o',ms=3,mfc='w',mec=self.colb)
        self.ax.set_xlim((self.latlims[0], self.latlims[1]))
        self.ax.set_ylim((self.hlims[0], self.hlims[1]))
        self.xs = list(self.sline.get_xdata())
        self.ys = list(self.sline.get_ydata())
        self.xb = list(self.bline.get_xdata())
        self.yb = list(self.bline.get_ydata())
        self.lastkey = '1'
        
        # connect to all the events we need
        self.cidpress = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidback = self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_press(self, event):
        'add a point on mouse click and update line'
        if self.lastkey == '1':
            self.xs.append(event.xdata)
            self.ys.append(event.ydata)
            self.sline.set_data(self.xs, self.ys)
            self.sline.figure.canvas.draw()
        elif self.lastkey == '2':
            self.xb.append(event.xdata)
            self.yb.append(event.ydata)
            self.bline.set_data(self.xb, self.yb)
            self.bline.figure.canvas.draw()
        
    def on_key(self, event):
        'delete the last point on backspace and update plot'
        if event.key == 'backspace':
            if self.lastkey == '1':
                del self.xs[-1]
                del self.ys[-1]
                self.sline.set_data(self.xs, self.ys)
                self.sline.figure.canvas.draw()
            elif self.lastkey == '2':
                del self.xb[-1]
                del self.yb[-1]
                self.bline.set_data(self.xb, self.yb)
                self.bline.figure.canvas.draw()
        elif event.key == 'n':
            if self.lastkey == '1':
                self.xs.append('nan')
                self.ys.append('nan')
                self.sline.set_data(self.xs, self.ys)
                self.sline.figure.canvas.draw()
            elif self.lastkey == '2':
                self.xb.append('nan')
                self.yb.append('nan')
                self.bline.set_data(self.xb, self.yb)
                self.bline.figure.canvas.draw()
        else:
            self.lastkey = event.key
            if event.key == '1':
                col = self.cols
                tit = "EDITING THE POND SURFACE: click to select points\npress '2' to edit the lake bed\npress 'backspace' to delete last point or 'n' to start a new line segment"
            elif event.key == '2':
                col = self.colb
                tit = "EDITING THE LAKE BED: click to select points\npress '1' to edit the surface\npress 'backspace' to delete last point or 'n' to start a new line segment"
            else:
                col = 'k'
                tit = "invalid keyboard input\npress '1' to edit the surface or '2' to edit the lake bed"
                    
            self.ax.set_title(tit,color=col)
            self.ax.spines['bottom'].set_color(col)
            self.ax.spines['left'].set_color(col)
            self.ax.spines['top'].set_color(col)
            self.ax.spines['right'].set_color(col)
            self.ax.xaxis.label.set_color(col)
            self.ax.yaxis.label.set_color(col)
            self.ax.tick_params(axis='x', colors=col)
            self.ax.tick_params(axis='y', colors=col)
            event.canvas.draw()
            
def getDataDownload(pond1,pond2,pond3,pond4,YOUR_NAME):
    
    import pandas as pd
    import os
    import matplotlib.pylab as plt
    import numpy as np
    
    lat = np.array([])
    h = np.array([])
    pondid = np.array([])
    typeid = np.array([])
    ponddata = [pond1, pond2, pond3, pond4]
    for ipond,p in enumerate(ponddata):
        s1 = [p.xs, p.ys]
        s2 = [p.xb, p.yb]
        for itype,s in enumerate([s1, s2]):
            lat = np.append(lat,s[0])
            h = np.append(h,s[1])
            pondid = np.append(pondid,np.ones((len(s[0]),1))*(ipond+1))
            typeid = np.append(typeid,np.ones((len(s[0]),1))*(itype+1))
    
    df = pd.DataFrame({'lat': lat, 'h': h, 'pondid': pondid, 'typeid': typeid})
    df = df.astype({'lat': float, 'h': float, 'pondid': int, 'typeid': int})
    
    # plot all data
    fig = plt.figure(figsize=[7, 4.8])
    for ipond,p in enumerate(ponddata):
        thispond = ipond+1
        issurf = (df.pondid == thispond) & (df.typeid == 1)
        isbott = (df.pondid == thispond) & (df.typeid == 2)
        xsurf = df.lat[issurf]
        ysurf = df.h[issurf]
        xbott = df.lat[isbott]
        ybott = df.h[isbott]
        ax = fig.add_subplot(2,2,thispond)
        ax.set_title('pond' + str(thispond) + ', ' + YOUR_NAME,size=8)
        ax.set_xlabel('latitude',size=8)
        ax.set_ylabel('elevation [m]',size=8)
        ax.tick_params(axis='both', which='major', labelsize=6)
        ax.scatter(p.lat_ph,p.h_ph,s=10,c=p.colph,alpha=0.2,edgecolors='none')
        ax.plot(xsurf,ysurf,c='b')
        ax.plot(xbott,ybott,c='r')
        ax.set_xlim((p.latlims[0], p.latlims[1]))
        ax.set_ylim((p.hlims[0], p.hlims[1]))
    fig.tight_layout()
    
    outname = 'pickeddata/pondPicking-' + YOUR_NAME + '.csv'
    if not os.path.exists('pickeddata'):
        os.makedirs('pickeddata')
    df.to_csv(outname, index=False)