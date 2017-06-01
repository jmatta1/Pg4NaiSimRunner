void merge_hists()
{
    //Open the file that will hold the merged histograms
    TFile* outFile = new TFile("response.root","RECREATE");
    //open the files created by simulation
    TFile* file1 = new TFile("side0.root");
    TFile* file2 = new TFile("side2.root");
    TFile* file3 = new TFile("side4.root");
    //retrieve the histograms originally created by simulation
    TH1D* hist1 = (TH1D*)file1->Get("scint_eioni");
    TH1D* hist2 = (TH1D*)file2->Get("scint_eioni");
    TH1D* hist3 = (TH1D*)file3->Get("scint_eioni");
    // create the hisogram that will have the unnormalized response function
    outFile->cd();
    TH1D* sum_hist = (TH1D*)hist1->Clone();
    sum_hist->SetNameTitle("SumResp","Sum Response");
    sum_hist->Add(hist1, hist2, 1.0, 1.0);
    sum_hist->Add(hist3, 1.0);
    outFile->cd();
    sum_hist->Write();
    delete sum_hist;
    // create the hisogram that will have the normalized response function
    outFile->cd();
    sum_hist = (TH1D*)hist1->Clone();
    sum_hist->SetNameTitle("NormSumResp","Normalized Sum Response");
    // The number of counts thrown at each side was scaled to the surface area
    // of each side by dividing each histogram by the number of primaries
    // and multiplying by the fraction of the total area accounted for by side
    // for which the histogram was generated
    // areas 
    sum_hist->Add(hist1, hist2, 0.599566/(11050000.0), 0.317417/(5850000.0));
    sum_hist->Add(hist3, 0.0830168/(3.0*1530000.0));
    outFile->cd();
    sum_hist->Write();
    delete sum_hist;
    // create a TF1 for later use
    TF1* unity = new TF1("unity","1",-1.0,100000000.0);
    // now create the histogram with the normalized large front face response
    outFile->cd();
    TH1D* face_resp = (TH1D*)hist1->Clone();
    face_resp->SetName("NormLargeFaceFront");
    face_resp->Multiply(unity, 1.0/11050000.0);
    outFile->cd();
    face_resp->Write();
    delete face_resp;
    //now write out the unnormalized large front face response
    outFile->cd();
    hist1->SetName("LargeFaceFront");
    hist1->Write();
    delete hist1;
    // now create the histogram with the normalized medium front face response
    outFile->cd();
    face_resp = (TH1D*)hist2->Clone();
    face_resp->SetName("NormMediumFaceFront");
    face_resp->Multiply(unity, 1.0/5850000.0);
    outFile->cd();
    face_resp->Write();
    delete face_resp;
    //now write out the unnormalized medium front face response
    outFile->cd();
    hist2->SetName("MediumFaceFront");
    hist2->Write();
    delete hist2;
    // now create the histogram with the normalized small front face response
    outFile->cd();
    face_resp = (TH1D*)hist3->Clone();
    face_resp->SetName("NormSmallFaceFront");
    face_resp->Multiply(unity, 1.0/1530000.0);
    outFile->cd();
    face_resp->Write();
    delete face_resp;
    //now write out the unnormalized small front face response
    outFile->cd();
    hist3->SetName("SmallFaceFront");
    hist3->Write();
    delete hist3;
    //now flush the file to be sure there is nothing in the buffer
    outFile->Flush();
    //now delete the TF1 since we no longer need it
    delete unity;
    //now delete all the files
    delete file1;
    delete file2;
    delete file3;
    delete outFile;
}
