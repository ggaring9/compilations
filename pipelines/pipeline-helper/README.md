Pipeline Helper

Bunch of Python scripts that is used for some Gitlab-CI Pipeline jobs (i.e. composer, upload to artifactory, trigger Ansible Tower job, etc.). This was created initially by the Environment team (c/o Massimo and Eric V.), we just made it easier to use across multiple projects.


Usage



Add this as a git submodule on your project under the automation folder.

git submodule add ../../CMS/pipeline-helper.git automation/pipeline-helper

Make sure to enable the GIT_SUBMODULE_STRATEGY: recursive variable on your app's .gitlab-ci.yml.

Create automation/pipeline.json on your app to define the tasks you need to run on your Gitlab-CI jobs.

{
        "artifactory": {
            "username": "$CI_PROJECT_NAME",
            "password": "$ARTIFACTORY_PASSWORD",
            "permissions": [
                "r",
                "w"
            ],
            "instances": [
                "http://trc-ptc-afact01.msred.dom:8081/artifactory/$CI_PROJECT_NAME"
            ]
        },
        "package": {
            "steps": {
                "composer": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.composer",
                    "docker-image-suffix": "-composer",
                    "options": [],
                    "command": [
                        "install",
                        "-v",
                        "--no-interaction"
                    ],
                    "volumes": [
                        "$PWD:/var/www/html/app"
                    ]
                },
                "yarn-install": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.yarn",
                    "docker-image-suffix": "-yarn",
                    "options": [
                        "--env",
                        "DIRPATH=/app/devtool/"
                    ],
                    "command": [
                        "yarn",
                        "install"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "yarn-dist": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.yarn",
                    "docker-image-suffix": "-yarn",
                    "options": [
                        "--env",
                        "DIRPATH=/app/devtool/"
                    ],
                    "command": [
                        "yarn",
                        "run",
                        "dist"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "package": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.package",
                    "docker-image-suffix": "-package",
                    "options": [
                        "--env", "CI_PROJECT_NAME=$CI_PROJECT_NAME",
                        "--env", "VERSION=$VERSION",
                        "--env", "CI_PIPELINE_ID=$CI_PIPELINE_ID",
                        "--env", "ARTIFACTORY_PASSWORD=$ARTIFACTORY_PASSWORD"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/package.py",
                        "--configuration-file",
                        "/app/automation/pipeline-helper/package.json"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/package.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "sonarqube": {
            "steps": {
                "sonarqube-scanner": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.sonarqube",
                    "docker-image-suffix": "-sonarqube:1.0.0",
                    "options": [],
                    "command": [
                        "/sonar-scanner/bin/sonar-scanner",
                        "-Dsonar.host.url=$SONARQUBE_URL",
                        "-Dsonar.projectKey=$CI_PROJECT_NAME",
                        "-Dsonar.sources=./",
                        "-Dsonar.projectVersion=$VERSION"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "deploy-development": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$MSGREEN_AUTHORIZED_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/package.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "deploy": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.deploy",
                    "docker-image-suffix": "-deploy",
                    "options": [
                        "--env",
                        "TC_USERNAME=dafa-stack",
                        "--env",
                        "TC_PASSWORD=$MSGREEN_DEPLOY_PASSWORD",
                        "--env",
                        "TC_HOST=mic-tst-itass01.msgreen.dom",
                        "--env",
                        "TC_VERIFY_SSL=no",
                        "--env",
                        "TC_RECKLESS_MODE=yes"
                    ],
                    "command": [
                        "kick_and_monitor",
                        "--template-name",
                        "CMS: deploy - development environment",
                        "--extra-vars",
                        "version: $VERSION.$CI_PIPELINE_ID",
                        "--extra-vars",
                        "project: $CI_PROJECT_NAME"
                    ],
                    "volumes": []
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/development.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "integration-tests-development": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$MSGREEN_AUTHORIZED_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/development.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "trigger integration tests": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.deploy",
                    "docker-image-suffix": "-integration-tests",
                    "options": [
                        "--env",
                        "TC_USERNAME=dafa-stack",
                        "--env",
                        "TC_PASSWORD=$INTEGRATION_TESTS_PASSWORD",
                        "--env",
                        "TC_HOST=msc-co-itass01.msorange.dom",
                        "--env",
                        "TC_VERIFY_SSL=no",
                        "--env",
                        "TC_RECKLESS_MODE=yes"
                    ],
                    "command": [
                        "kick_and_monitor",
                        "--template-name",
                        "Execute selenium integration tests",
                        "--extra-vars",
                        "version: $VERSION.$CI_PIPELINE_ID",
                        "--extra-vars",
                        "project: $CI_PROJECT_NAME",
                        "--extra-vars",
                        "test_type: build-sanity",
                        "--extra-vars",
                        "gitlab_user_email: $GITLAB_USER_EMAIL"
                    ],
                    "volumes": []
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/integration-tests-development.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "deploy-testing": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$MSGREEN_AUTHORIZED_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/development.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "deploy": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.deploy",
                    "docker-image-suffix": "-deploy",
                    "options": [
                        "--env",
                        "TC_USERNAME=dafa-stack",
                        "--env",
                        "TC_PASSWORD=$MSGREEN_DEPLOY_PASSWORD",
                        "--env",
                        "TC_HOST=mic-tst-itass01.msgreen.dom",
                        "--env",
                        "TC_VERIFY_SSL=no",
                        "--env",
                        "TC_RECKLESS_MODE=yes"
                    ],
                    "command": [
                        "kick_and_monitor",
                        "--template-name",
                        "CMS: deploy - testing environment (QA)",
                        "--extra-vars",
                        "version: $VERSION.$CI_PIPELINE_ID",
                        "--extra-vars",
                        "project: $CI_PROJECT_NAME"
                    ],
                    "volumes": []
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/testing.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "integration-tests-test": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$MSGREEN_AUTHORIZED_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/testing.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "trigger integration tests": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.deploy",
                    "docker-image-suffix": "-integration-tests",
                    "options": [
                        "--env",
                        "TC_USERNAME=dafa-stack",
                        "--env",
                        "TC_PASSWORD=$INTEGRATION_TESTS_PASSWORD",
                        "--env",
                        "TC_HOST=msc-co-itass01.msorange.dom",
                        "--env",
                        "TC_VERIFY_SSL=no",
                        "--env",
                        "TC_RECKLESS_MODE=yes"
                    ],
                    "command": [
                        "kick_and_monitor",
                        "--template-name",
                        "Execute selenium integration tests",
                        "--extra-vars",
                        "version: $VERSION.$CI_PIPELINE_ID",
                        "--extra-vars",
                        "project: $CI_PROJECT_NAME",
                        "--extra-vars",
                        "test_type: full-regression",
                        "--extra-vars",
                        "gitlab_user_email: $GITLAB_USER_EMAIL"
                    ],
                    "volumes": []
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/integration-tests-test.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "deploy-tct": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$MSGREEN_AUTHORIZED_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/development.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "deploy": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.deploy",
                    "docker-image-suffix": "-deploy",
                    "options": [
                        "--env",
                        "TC_USERNAME=dafa-stack",
                        "--env",
                        "TC_PASSWORD=$MSGREEN_DEPLOY_PASSWORD",
                        "--env",
                        "TC_HOST=mic-tst-itass01.msgreen.dom",
                        "--env",
                        "TC_VERIFY_SSL=no",
                        "--env",
                        "TC_RECKLESS_MODE=yes"
                    ],
                    "command": [
                        "kick_and_monitor",
                        "--template-name",
                        "CMS: deploy - TCT environment",
                        "--extra-vars",
                        "version: $VERSION.$CI_PIPELINE_ID",
                        "--extra-vars",
                        "project: $CI_PROJECT_NAME"
                    ],
                    "volumes": []
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/testing.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "deploy-uat": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$MSORANGE_AUTHORIZED_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/testing.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "deploy": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.deploy",
                    "docker-image-suffix": "-deploy",
                    "options": [
                        "--env",
                        "TC_USERNAME=dafa-stack",
                        "--env",
                        "TC_PASSWORD=$MSORANGE_DEPLOY_PASSWORD",
                        "--env",
                        "TC_HOST=msc-co-itass01.msorange.dom",
                        "--env",
                        "TC_VERIFY_SSL=no",
                        "--env",
                        "TC_RECKLESS_MODE=yes"
                    ],
                    "command": [
                        "kick_and_monitor",
                        "--template-name",
                        "CMS: deploy - uat environment",
                        "--extra-vars",
                        "version: $VERSION.$CI_PIPELINE_ID",
                        "--extra-vars",
                        "project: $CI_PROJECT_NAME"
                    ],
                    "volumes": []
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/uat.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "deploy-staging": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$MSORANGE_AUTHORIZED_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/testing.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "deploy": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.deploy",
                    "docker-image-suffix": "-deploy",
                    "options": [
                        "--env",
                        "TC_USERNAME=dafa-stack",
                        "--env",
                        "TC_PASSWORD=$MSORANGE_DEPLOY_PASSWORD",
                        "--env",
                        "TC_HOST=msc-co-itass01.msorange.dom",
                        "--env",
                        "TC_VERIFY_SSL=no",
                        "--env",
                        "TC_RECKLESS_MODE=yes"
                    ],
                    "command": [
                        "kick_and_monitor",
                        "--template-name",
                        "CMS: deploy - staging environment",
                        "--extra-vars",
                        "version: $VERSION.$CI_PIPELINE_ID",
                        "--extra-vars",
                        "project: $CI_PROJECT_NAME"
                    ],
                    "volumes": []
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/staging.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        },
        "staging-signoff": {
            "steps": {
                "authorize": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-authorize",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "AUTHORIZED_USERS=$STAGING_SIGNOFF_USERS",
                        "--env",
                        "DEPENDS_ON=/app/automation/pipeline-helper/deployed/staging.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/script/authorize.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                },
                "mark as complete": {
                    "dockerfile": "automation/pipeline-helper/Dockerfile.authorize",
                    "docker-image-suffix": "-mark-as-complete",
                    "options": [
                        "--env",
                        "USER=$GITLAB_USER_EMAIL",
                        "--env",
                        "CREATES=/app/automation/pipeline-helper/deployed/staging-signoff.jsonl"
                    ],
                    "command": [
                        "python",
                        "/app/automation/pipeline-helper/mark_as_complete.py"
                    ],
                    "volumes": [
                        "$PWD:/app"
                    ]
                }
            }
        }
}


Create automation/package.json on your app to define the files and folders that will be included on your package to be uploaded to the artifactory.

{
        "include_directories": [
            "app",
            "assets",
            "cache",
            "core",
            "devtool",
            "logs",
            "src",
            "templates",
            "vendor",
            "web"
        ],
        "exclude_directories": [
            ".git",
            ".svn",
            "build",
            "deploy",
            "example",
            "test",
            "tests"
        ],
        "exclude_extensions": [
            "txt",
            "TXT",
            "CHANGELOG.md",
            "README",
            "README.md",
            "LICENSE",
            "example.settings.local.php",
            "example.sites.php",
            ".gitkeep",
            "composer.json"
        ]
}



Use the tasks you defined on your pipeline.json in your .gitlab-ci.yml (put it on the script section of your job).

script:
    - python -u automation/pipeline-helper/run.py --stage sonarqube
