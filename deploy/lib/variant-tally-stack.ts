import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import { TallyConstruct } from "./tally-construct";
import { Vpc } from "aws-cdk-lib/aws-ec2";

export type VariantTallyProps = {};

export class VariantTallyStack extends cdk.Stack {
  constructor(
    scope: Construct,
    id: string,
    stackProps: cdk.StackProps,
    constructProps: VariantTallyProps,
  ) {
    super(scope, id, stackProps);

    const vpc = Vpc.fromLookup(this, "Vpc", {
      vpcName: "main-vpc",
    });

    const tally = new TallyConstruct(this, "Tally", {
      labs: {
        Lab1: {
          accountNumber: "602836945884",
          bucketName: "variant-tally-example-lab-1",
        },
        Lab2: {
          accountNumber: "602836945884",
          bucketName: "variant-tally-example-lab-2",
        },
      },
    });
  }
}
