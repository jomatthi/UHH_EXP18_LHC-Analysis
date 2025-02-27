import os
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = 2002


class Plotter(object):
    """
    A plotter to produce .pdf files from the histograms stored in the output.root files.
    """

    def __init__(self, analyzers):
        # set default plotting style
        self.style = default_style()
        self.style.SetOptLogy(True)
        ROOT.gROOT.SetStyle("MyStyle");
        self.colors = {'TTbar': 632, 'single top': 798, 'W+jets': 602, 'QCD': 867, 'DY+jets': 829, 'Diboson': 875}
        self.hists_data = []
        self.hists_stack = []
        self.hists_err = []
        if not os.path.exists('plots'):
            os.makedirs('plots')
        # loop over all histograms
        # apply dataset specific styling and create THStack and TH1 objects for plotting
        for process in analyzers.keys():
            i = 0
            is_data = ('data' in process.lower())
            for d in analyzers[process].histograms.keys():
                for hist in analyzers[process].histograms[d].hists.values():
                    if not is_data:
                        if process in self.colors.keys():
                            hist.SetFillColor(self.colors[process])
                        if i >= len(self.hists_stack):
                            self.hists_stack.append(ROOT.THStack(hist.GetName() + "_stack", hist.GetTitle()))
                            self.hists_err.append(hist.Clone(hist.GetName() + "_err"))
                            self.hists_err[i].SetTitle("stat. Uncert.")
                            self.hists_err[i].Reset()
                            self.hists_err[i].SetFillColor(923)
                            self.hists_err[i].SetFillStyle(3005)
                            self.hists_err[i].SetLineWidth(0)                            
                        hist.SetTitle(process)
                        self.hists_stack[i].Add(hist)
                        self.hists_err[i].Add(hist)
                    else:
                        hist.SetTitle(process)
                        hist.SetMarkerStyle(20)
                        hist.SetMarkerColor(1)
                        self.hists_data.append(hist)
                    i += 1

# self.histograms = {d:{{process:hist} for process in analyzers.keys()] for d in dirs}

    def process(self):
        s = ""
        for i in range(0, len(self.hists_stack)):
            h = self.hists_stack[i]
            c = ROOT.TCanvas("c", "c", 800, 600)
            if h.GetMaximum() <= 0: h.SetMaximum(1)
            h.SetMinimum(0.8)
            h.Draw("hist")
            h.GetXaxis().SetTitle(h.GetTitle())
            h.GetXaxis().SetTitleOffset(1.3)
            h.GetYaxis().SetTitle("Events")
            h.GetYaxis().SetTitleOffset(1.3)
            c.Modified()
            self.hists_err[i].Draw("E2SAME")
            c.Modified()
            c.BuildLegend(0.76, 0.4, 0.95, 0.95, "");
            c.Print("plots/"+"_".join(h.GetName().split("_")[1:])+"_MC.pdf")
            if len(self.hists_data) > 0:
                self.hists_data[i].Draw("PESAME")
                c.BuildLegend(0.75, 0.35, 0.95, 0.95, "");
                c.Print("plots/"+"_".join(h.GetName().split("_")[1:])+".pdf")

            old_s = s
            s = "_".join(h.GetName().split("_")[1:])
            s = "".join(s.split("_default")[0:1])+".pdf"
            if (s != old_s):
                if (i == len(self.hists_stack) - 1):
                    c.Print(s)
                else:
                    c.Print(s+"(")
                if (old_s != ""):
                    c.Print(old_s+"]")
            elif (i == len(self.hists_stack) - 1):
                c.Print(s+")")
            else:
                c.Print(s)
            del c


def default_style():
    """
    default plotting style based on old LHCTop code.
    """
    MyStyle = ROOT.TStyle("MyStyle", "My Root Style");
    MyStyle.SetStatColor(0);
    MyStyle.SetCanvasColor(0);
    MyStyle.SetPadColor(0);
    MyStyle.SetPadBorderMode(0);
    MyStyle.SetCanvasBorderMode(0);
    MyStyle.SetFrameBorderMode(0);
    MyStyle.SetOptTitle(0);
    MyStyle.SetOptStat(0);
    MyStyle.SetStatBorderSize(2);
    MyStyle.SetOptTitle(0);
    MyStyle.SetPadTickX(1);
    MyStyle.SetPadTickY(1);
    MyStyle.SetPadBorderSize(2);
    MyStyle.SetPalette(51);
    MyStyle.SetPadBottomMargin(0.15);
    MyStyle.SetPadTopMargin(0.05);
    MyStyle.SetPadLeftMargin(0.15);
    MyStyle.SetPadRightMargin(0.25);
    MyStyle.SetLineWidth(1);
    MyStyle.SetHistLineWidth(3);
    MyStyle.SetLegendBorderSize(0);
    MyStyle.SetNdivisions(505, "x");
    MyStyle.SetMarkerSize(0.8);
    MyStyle.SetTickLength(0.03);
    MyStyle.SetTitleOffset(1.5, "x");
    # modified
    MyStyle.SetTitleOffset(2.0, "y");
    #
    MyStyle.SetTitleOffset(1.0, "z");
    MyStyle.SetLabelSize(0.05, "x");
    MyStyle.SetLabelSize(0.05, "y");
    MyStyle.SetLabelSize(0.05, "z");
    MyStyle.SetLabelOffset(0.03, "x");
    MyStyle.SetLabelOffset(0.03, "y");
    MyStyle.SetLabelOffset(0.03, "z");
    MyStyle.SetTitleSize(0.05, "x");
    MyStyle.SetTitleSize(0.05, "y");
    MyStyle.SetTitleSize(0.05, "z");
    MyStyle.SetTickLength(0.02, "x");
    return MyStyle
