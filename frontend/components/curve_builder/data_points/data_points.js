
export function defaultDataPoint(type) {
    // Return default data point object for a given type
    let dataPoint = {};

    switch (type) {

        case 'CpiLevelDataPoint':
            dataPoint = { type: 'CpiLevelDataPoint', date: undefined, value: undefined, isActive: true };
            break;

        case 'YoYDataPoint':
            dataPoint = { type: 'YoYDataPoint', start_date: undefined, tenor: undefined, value: undefined, isActive: true };
            break;

        case 'AdditiveSeasonalityDataPoint':
            dataPoint = { type: 'AdditiveSeasonalityDataPoint', month_str: undefined, value: undefined, isActive: true }
            break;

        default:
            // unexpected
            console.log('Unexpected data point type ' + type);

    }
    return dataPoint;
};
