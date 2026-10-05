// Usage:
// root -l 'check_dataset.C+("../../build/layer_signals.root")'

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TGaxis.h"
#include "TH1D.h"
#include "TLatex.h"
#include "TPaveText.h"
#include "TStyle.h"
#include "TTree.h"

constexpr int NumberOfLayers = 180;
constexpr int NumberOfEnergyBins = 50;

constexpr double EnergyMin = 0.1;
constexpr double EnergyMax = 500.0;

constexpr double LayerThicknessCm = 0.5;

void check_dataset(const char *filename = "layer_signals.root") {

  TFile *file = TFile::Open(filename, "READ");

  if (!file || file->IsZombie()) {
    std::cerr << "Error: cannot open file " << filename << std::endl;
    return;
  }

  TTree *tree = nullptr;
  file->GetObject("LayerSignals", tree);

  if (!tree) {
    std::cerr << "Error: TTree 'LayerSignals' not found." << std::endl;

    file->Close();
    delete file;
    return;
  }

  Int_t event = 0;
  Int_t nPrimaryGammas = 0;

  Double_t totalPrimaryEnergy = 0.0;
  Double_t generatedMean = 0.0;
  Double_t generatedSigma = 0.0;

  std::vector<double> *layerEdep = nullptr;
  std::vector<double> *gammaSpectrum = nullptr;

  tree->SetBranchAddress("event", &event);
  tree->SetBranchAddress("n_primary_gammas", &nPrimaryGammas);

  tree->SetBranchAddress("total_primary_energy_MeV", &totalPrimaryEnergy);

  tree->SetBranchAddress("generated_mean_MeV", &generatedMean);

  tree->SetBranchAddress("generated_sigma_MeV", &generatedSigma);

  tree->SetBranchAddress("layer_edep_MeV", &layerEdep);

  tree->SetBranchAddress("gamma_spectrum", &gammaSpectrum);

  gStyle->SetOptStat(0);

  const Long64_t nEntries = tree->GetEntries();
  const Long64_t nEventsToSave = std::min<Long64_t>(10, nEntries);

  for (Long64_t entry = 0; entry < nEventsToSave; ++entry) {

    tree->GetEntry(entry);

    if (!gammaSpectrum || !layerEdep) {
      std::cerr << "Error: null vector at entry " << entry << std::endl;
      continue;
    }

    // Check vector dimensions
    if (layerEdep->size() != NumberOfLayers) {
      std::cerr << "Warning: event " << event << " has " << layerEdep->size()
                << " layers instead of " << NumberOfLayers << std::endl;
    }

    if (gammaSpectrum->size() != NumberOfEnergyBins) {
      std::cerr << "Warning: event " << event << " has "
                << gammaSpectrum->size() << " energy bins instead of "
                << NumberOfEnergyBins << std::endl;
    }

    std::cout << "Event " << event << " | N_gamma = " << nPrimaryGammas
              << " | E_primary = " << totalPrimaryEnergy << " MeV" << std::endl;

    // ============================================================
    // Event canvas: primary spectrum + longitudinal energy deposition
    // ============================================================

    TCanvas canvas(Form("cEvent_%d", event), "Event overview", 1000, 1100);

    canvas.Divide(1, 2);

    // ============================================================
    // Top pad: primary gamma spectrum
    // ============================================================

    canvas.cd(1);

    gPad->SetTopMargin(0.12);
    gPad->SetBottomMargin(0.04);

    TH1D spectrum("spectrum", "", NumberOfEnergyBins, EnergyMin, EnergyMax);

    for (size_t i = 0; i < gammaSpectrum->size() &&
                       i < static_cast<size_t>(NumberOfEnergyBins);
         ++i) {

      spectrum.SetBinContent(static_cast<int>(i) + 1, gammaSpectrum->at(i));
    }

    spectrum.GetXaxis()->SetTitle("Primary gamma energy [MeV]");

    spectrum.GetYaxis()->SetTitle("Number of gammas");

    spectrum.SetLineWidth(2);

    spectrum.Draw("HIST");

    // Event information
    TPaveText info(0.25, 0.93, 0.75, 0.995, "NDC");

    info.SetFillStyle(0);
    info.SetBorderSize(0);
    info.SetTextAlign(22);
    info.SetTextSize(0.035);

    info.AddText(Form("Event %d   N_{#gamma} = %d", event, nPrimaryGammas));

    info.Draw();

    // ============================================================
    // Bottom pad: longitudinal deposited energy
    // ============================================================

    canvas.cd(2);

    gPad->SetTopMargin(0.1);
    gPad->SetBottomMargin(0.12);

    TH1D layers("layers", "", NumberOfLayers, 0.5, NumberOfLayers + 0.5);

    for (size_t i = 0;
         i < layerEdep->size() && i < static_cast<size_t>(NumberOfLayers);
         ++i) {

      layers.SetBinContent(static_cast<int>(i) + 1, layerEdep->at(i));
    }

    layers.GetXaxis()->SetTitle("Layer number");

    layers.GetYaxis()->SetTitle("Deposited energy [MeV]");

    layers.SetLineWidth(2);

    layers.Draw("HIST");

    // Make sure pad coordinates are updated before creating TGaxis
    gPad->Update();

    // ============================================================
    // Top X-axis: detector depth in cm
    // ============================================================

    const double depthMaxCm = NumberOfLayers * LayerThicknessCm;

    TGaxis depthAxis(0.5, gPad->GetUymax(), NumberOfLayers + 0.5,
                     gPad->GetUymax(), 0.0, depthMaxCm, 510, "+");

    depthAxis.SetLabelSize(0.032);

    // Move depth numbers above the axis line.
    depthAxis.SetLabelOffset(-0.035);

    // Short ticks.
    depthAxis.SetTickSize(0.018);

    depthAxis.SetNdivisions(9);

    TLatex depthTitle;

    depthTitle.SetNDC();
    depthTitle.SetTextAlign(22);
    depthTitle.SetTextSize(0.032);

    depthTitle.DrawLatex(0.50, 0.97, "Depth [cm]");

    depthAxis.Draw();
    // ============================================================
    // Save complete event canvas
    // ============================================================

    canvas.Modified();
    canvas.Update();

    std::ostringstream outputName;

    outputName << "event_" << std::setw(3) << std::setfill('0') << event
               << "_overview.png";

    canvas.SaveAs(outputName.str().c_str());

    std::cout << "Saved: " << outputName.str() << std::endl;
  }

  // Close file only after processing all events
  file->Close();
  delete file;

  std::cout << "\nFinished. Saved " << nEventsToSave << " PNG files."
            << std::endl;
}
