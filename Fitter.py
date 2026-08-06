import ROOT


class Fitter(object):

    def __init__(self, analyzers):
        self.top_hist_MC = 0
        self.top_hist = 0
        for x in analyzers:
            if (x == 'Data'):
                self.top_hist = analyzers[x].histograms['top_mass'].hists['top_mass']  # noqa
            elif (self.top_hist_MC == 0):
                self.top_hist_MC = analyzers[x].histograms['top_mass'].hists['top_mass']  # noqa
            else:
                self.top_hist_MC.Add(analyzers[x].histograms['top_mass'].hists['top_mass'])  # noqa
        self.mean = 0.0
        self.unc = 0.0
        self.output_dir = analyzers['TTbar'].output_dir

    def fit(self, fit_min, fit_max):
        MyStyle = ROOT.TStyle("MyStyle1", "My Root Style1")
        MyStyle.SetOptStat(0)
        MyStyle.SetOptFit(1)
        MyStyle.SetOptLogy(False)
        ROOT.gROOT.SetStyle("MyStyle1")
        if (not self.top_hist == 0):
            c = ROOT.TCanvas()
            self.top_hist.Draw()
            self.top_hist.Fit("gaus", "Q", "", fit_min, fit_max)
            fit = self.top_hist.GetFunction("gaus")
            self.mean = fit.GetParameter(1)
            self.unc = fit.GetParError(1)
            print(
                "Fitted reconstructed top-mass coordinate in data: "
                f"{self.mean:.3f} +- {self.unc:.3f} blinded units"
            )
            print(f'With {str(self.top_hist.GetEntries())} top quark candidates')  # noqa
            c.SaveAs(f"{self.output_dir}/ReconstructedTopMass_blinded.pdf")
            del c

        # c = ROOT.TCanvas()
        # self.top_hist_MC.Draw()
        # self.top_hist_MC.Fit("gaus", "Q", "", fit_min, fit_max)
        # fit = self.top_hist_MC.GetFunction("gaus")
        # self.mean = fit.GetParameter(1)
        # self.unc = fit.GetParError(1)
        # print('\n\n------------------------------------------------------')
        # print(
        #     "Fitted reconstructed top-mass coordinate in MC: "
        #     f"{self.mean:.3f} +- {self.unc:.3f} blinded units"
        # )
        # print(f'With {str(self.top_hist_MC.GetEntries())} top quark candidates')  # noqa
        # c.SaveAs(f"{self.output_dir}/ReconstructedTopMass_blinded_MC.pdf")
        # del c
        return self.top_hist
