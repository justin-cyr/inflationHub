
const protobuf = require("protobufjs");

export async function decodePricingData(base64str) {
    const proto = await protobuf.load("PricingData.proto")
    const PricingData = proto.lookupType("PricingData")
    const byteArray = Uint8Array.from(atob(base64str), (m) => m.codePointAt(0));

    // verify
    const errorMsg = PricingData.verify(byteArray);
    if (errorMsg) {
        throw Error(errorMsg);
    }

    // decode
    const message = PricingData.decode(byteArray);
    console.log(message);

    return PricingData.toObject(message);
};

