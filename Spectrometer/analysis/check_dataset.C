// Usage:
// root -l 'check_dataset.C+("../../build/layer_signals.root")'

#include <algorithm>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <vector>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1D.h"
#include "TPaveText.h"
#include "TStyle.h"
#include "TTree.h"

constexpr int NumberOfLayers = 90;
constexpr int NumberOfEnergyBins = 100;

constexpr double EnergyMin = 0.1;
constexpr double EnergyMax = 100.0;

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

    std::cout << "Event " << event << " | N_gamma = " << nPrimaryGammas
              << " | E_primary = " << totalPrimaryEnergy << " MeV"
              << " | mu = " << generatedMean << " MeV"
              << " | sigma = " << generatedSigma << " MeV" << std::endl;

    // ============================================================
    // Primary gamma spectrum
    // ============================================================

    {
      TCanvas canvas(Form("cSpectrum_%d", event), "Primary gamma spectrum",
                     1000, 700);

      // Leave enough space at the top for the information box.
      canvas.SetTopMargin(0.16);

      TH1D spectrum("spectrum", "", NumberOfEnergyBins, EnergyMin, EnergyMax);

      for (size_t i = 0; i < gammaSpectrum->size(); ++i) {

        spectrum.SetBinContent(static_cast<int>(i) + 1, gammaSpectrum->at(i));
      }

      spectrum.GetXaxis()->SetTitle("Primary gamma energy [MeV]");

      spectrum.GetYaxis()->SetTitle("Number of gammas");

      spectrum.SetLineWidth(2);

      // Draw the histogram FIRST.
      spectrum.Draw("HIST");

      // Draw the event information AFTER the histogram.
      TPaveText info(0.25, 0.92, 0.75, 0.995, "NDC");

      info.SetFillStyle(0);
      info.SetBorderSize(0);
      info.SetTextAlign(22);
      info.SetTextSize(0.035);

      info.AddText(Form("Event %d   #mu = %.2f MeV   #sigma = %.2f MeV", event,
                        generatedMean, generatedSigma));

      info.Draw();

      canvas.Modified();
      canvas.Update();

      std::ostringstream outputName;

      outputName << "event_" << std::setw(3) << std::setfill('0') << event
                 << "_spectrum.png";

      canvas.SaveAs(outputName.str().c_str());

      std::cout << "Saved: " << outputName.str() << std::endl;
    }

    // ============================================================
    // Longitudinal deposited energy
    // ============================================================

    {
      TCanvas canvas(Form("cLayers_%d", event),
                     "Longitudinal energy deposition", 1000, 700);

      // Leave enough space at the top for the information box.
      canvas.SetTopMargin(0.16);

      TH1D layers("layers", "", NumberOfLayers, 0.5, NumberOfLayers + 0.5);

      for (size_t i = 0; i < layerEdep->size(); ++i) {

        layers.SetBinContent(static_cast<int>(i) + 1, layerEdep->at(i));
      }

      layers.GetXaxis()->SetTitle("Layer");

      layers.GetYaxis()->SetTitle("Deposited energy [MeV]");

      layers.SetLineWidth(2);

      // Draw the histogram FIRST.
      layers.Draw("HIST");

      // Draw the event information AFTER the histogram.
      TPaveText info(0.25, 0.92, 0.75, 0.995, "NDC");

      info.SetFillStyle(0);
      info.SetBorderSize(0);
      info.SetTextAlign(22);
      info.SetTextSize(0.035);

      info.AddText(Form("Event %d   #mu = %.2f MeV   #sigma = %.2f MeV", event,
                        generatedMean, generatedSigma));

      info.Draw();

      canvas.Modified();
      canvas.Update();

      std::ostringstream outputName;

      outputName << "event_" << std::setw(3) << std::setfill('0') << event
                 << "_layers.png";

      canvas.SaveAs(outputName.str().c_str());

      std::cout << "Saved: " << outputName.str() << std::endl;
    }
  }

  file->Close();
  delete file;

  std::cout << "\nFinished. Saved " << 2 * nEventsToSave << " PNG files."
            << std::endl;
}
