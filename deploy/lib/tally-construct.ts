import { Duration } from "aws-cdk-lib";
import { Construct } from "constructs";
import { PythonFunction } from "@aws-cdk/aws-lambda-python-alpha";
import { Runtime } from "aws-cdk-lib/aws-lambda";
import {
  Effect,
  ManagedPolicy,
  PolicyDocument,
  PolicyStatement,
  Role,
  ServicePrincipal,
} from "aws-cdk-lib/aws-iam";

export type LabProps = {
  accountNumber: string;
  bucketName: string;
};

export type QueryProps = {
  labs: Record<string, LabProps>;
};

/**
 * The tally construct represents a function that executes
 * on a regular basic computing tallies across labs.
 */
export class TallyConstruct extends Construct {
  public readonly fn: PythonFunction;

  constructor(scope: Construct, id: string, props: QueryProps) {
    super(scope, id);

    // we want to know the account numbers of all the labs as a set
    const allAccounts = new Set(
      Object.values(props.labs).map((l) => l.accountNumber),
    );

    const lambdaRole = new Role(this, "LambdaRole", {
      assumedBy: new ServicePrincipal("lambda.amazonaws.com"),
      managedPolicies: [
        // enough permissions to allow this to be run as a lambda
        ManagedPolicy.fromAwsManagedPolicyName(
          "service-role/AWSLambdaBasicExecutionRole",
        ),
      ],
      inlinePolicies: {
        // give this role the ability to limited read dynamo actions in the lab accounts
        S3WorkSharedAccounts: new PolicyDocument({
          statements: [
            new PolicyStatement({
              effect: Effect.ALLOW,
              actions: ["s3:*"],
              resources: ["*"],
              conditions: {
                StringEquals: {
                  "s3:ResourceAccount": Array.from(allAccounts),
                },
              },
            }),
          ],
        }),
      },
    });

    const env: Record<string, string> = {

    }

    // we construct a set of env variables to communicate to the lambda
    // our CDK configuration
    // note that the env variable names here must match the pattern in the Python lambda
    // (and vice versa)
    let labNumber = 0;

    for(const [n, l] of Object.entries(props.labs)) {
      env[`LAB_${labNumber}_NAME`] = n;
      env[`LAB_${labNumber}_BUCKET_NAME`] = l.bucketName;
      env[`LAB_${labNumber}_ACCOUNT_NUMBER`] = l.accountNumber;

      labNumber++;
    }

    this.fn = new PythonFunction(this, "TallyFunction", {
      role: lambdaRole,
      entry: "../tally-lambda",
      runtime: Runtime.PYTHON_3_12,
      timeout: Duration.minutes(1),
      // we run this so infrequently that there is no harm in giving it plenty of memory
      memorySize: 8192,
      // index: 'index.py', // optional, defaults to 'index.py'
      // handler: 'handler', // optional, defaults to 'handler'
      environment: env,
      bundling: {
        // image: new DockerImage("ghcr.io/astral-sh/uv:python3.12-bookworm"), // new DockerImage("public.ecr.aws/sam/build-python3.12:latest"),
        commandHooks: {
          beforeBundling(inputDir: string, outputDir: string): string[] {
            return [];
          },
          afterBundling(inputDir: string, outputDir: string): string[] {
            return [];
          },
        },
        // translates to `rsync --exclude='.venv' --exclude='__pycache__'`
        assetExcludes: [".venv", "__pycache__"],
      },
    });
  }
}
