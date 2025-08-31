#include <iostream>
#include <string>
using namespace std;

int main() {
    double ph, moisture, nitrogen;
    cin >> ph >> moisture >> nitrogen;  // Input from Flask

    string soilType;
    if (ph < 5.5) soilType = "Acidic Soil";
    else if (ph <= 7.5) soilType = "Neutral Soil";
    else soilType = "Alkaline Soil";

    string moistureLevel = (moisture < 30) ? "Dry" : "Moist";
    string fertility = (nitrogen < 50) ? "Low Fertility" : "High Fertility";

    cout << "Soil Type: " << soilType << "\n";
    cout << "Moisture Level: " << moistureLevel << "\n";
    cout << "Fertility: " << fertility << "\n";

    return 0;
}
