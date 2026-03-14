{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 8,
			"minor" : 6,
			"revision" : 4,
			"architecture" : "x64",
			"modernui" : 1
		},
		"classnamespace" : "box",
		"rect" : [ 100.0, 100.0, 650.0, 650.0 ],
		"bglocked" : 0,
		"openinpresentation" : 1,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"statusbarvisible" : 2,
		"toolbarvisible" : 1,
		"lefttoolbarpinned" : 0,
		"toptoolbarpinned" : 0,
		"righttoolbarpinned" : 0,
		"bottomtoolbarpinned" : 0,
		"toolbars_unpinned_last_save" : 0,
		"tallnewobj" : 0,
		"boxanimatetime" : 200,
		"enablehscroll" : 1,
		"enablevscroll" : 1,
		"devicewidth" : 400.0,
		"description" : "AI Sound Design Engine - prompt to preset retrieval and application",
		"digest" : "",
		"tags" : "",
		"style" : "",
		"subpatcher_template" : "",
		"assistshowspatchername" : 0,
		"boxes" : [
			{
				"box" : 				{
					"comment" : "Emits bang when device is fully loaded in Live",
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 400.0, 15.0, 120.0, 22.0 ],
					"text" : "live.thisdevice"
				}
			},
			{
				"box" : 				{
					"comment" : "JS bridge: 0=status, 1=result data, 2=score breakdown",
					"id" : "obj-2",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "" ],
					"patching_rect" : [ 140.0, 195.0, 200.0, 22.0 ],
					"text" : "js retrieve_and_apply.js"
				}
			},
			{
				"box" : 				{
					"id" : "obj-3",
					"maxclass" : "textedit",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "", "int", "", "" ],
					"patching_rect" : [ 20.0, 60.0, 300.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 32.0, 290.0, 24.0 ],
					"text" : "warm airy neo soul pad"
				}
			},
			{
				"box" : 				{
					"id" : "obj-4",
					"maxclass" : "textbutton",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 340.0, 60.0, 80.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 300.0, 32.0, 70.0, 24.0 ],
					"text" : "Generate"
				}
			},
			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "textbutton",
					"numinlets" : 1,
					"numoutlets" : 3,
					"outlettype" : [ "", "", "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 440.0, 60.0, 80.0, 24.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 300.0, 60.0, 70.0, 24.0 ],
					"text" : "Apply"
				}
			},
			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 20.0, 130.0, 130.0, 22.0 ],
					"text" : "prepend generate"
				}
			},
			{
				"box" : 				{
					"id" : "obj-7",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 440.0, 130.0, 50.0, 22.0 ],
					"text" : "apply"
				}
			},
			{
				"box" : 				{
					"id" : "obj-8",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 70.0, 255.0, 310.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 55.0, 92.0, 315.0, 22.0 ]
				}
			},
			{
				"box" : 				{
					"id" : "obj-9",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 6,
					"outlettype" : [ "", "", "", "", "", "" ],
					"patching_rect" : [ 200.0, 310.0, 380.0, 22.0 ],
					"text" : "route preset_name family style_cluster device_chain score"
				}
			},
			{
				"box" : 				{
					"id" : "obj-10",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 70.0, 370.0, 220.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 55.0, 118.0, 315.0, 22.0 ]
				}
			},
			{
				"box" : 				{
					"id" : "obj-11",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 70.0, 400.0, 220.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 55.0, 143.0, 315.0, 22.0 ]
				}
			},
			{
				"box" : 				{
					"id" : "obj-12",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 70.0, 430.0, 220.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 55.0, 168.0, 315.0, 22.0 ]
				}
			},
			{
				"box" : 				{
					"id" : "obj-13",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 70.0, 460.0, 220.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 55.0, 193.0, 315.0, 22.0 ]
				}
			},
			{
				"box" : 				{
					"id" : "obj-14",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 70.0, 490.0, 220.0, 22.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 55.0, 218.0, 315.0, 22.0 ]
				}
			},
			{
				"box" : 				{
					"id" : "obj-15",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 10.0, 200.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 5.0, 200.0, 22.0 ],
					"text" : "AI Preset Engine",
					"fontsize" : 14.0,
					"fontface" : 1
				}
			},
			{
				"box" : 				{
					"id" : "obj-16",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 255.0, 48.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 92.0, 48.0, 20.0 ],
					"text" : "Status:"
				}
			},
			{
				"box" : 				{
					"id" : "obj-17",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 370.0, 48.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 118.0, 48.0, 20.0 ],
					"text" : "Preset:"
				}
			},
			{
				"box" : 				{
					"id" : "obj-18",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 400.0, 48.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 143.0, 48.0, 20.0 ],
					"text" : "Family:"
				}
			},
			{
				"box" : 				{
					"id" : "obj-19",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 430.0, 48.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 168.0, 48.0, 20.0 ],
					"text" : "Cluster:"
				}
			},
			{
				"box" : 				{
					"id" : "obj-20",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 460.0, 48.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 193.0, 48.0, 20.0 ],
					"text" : "Chain:"
				}
			},
			{
				"box" : 				{
					"id" : "obj-21",
					"maxclass" : "comment",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 20.0, 490.0, 48.0, 20.0 ],
					"presentation" : 1,
					"presentation_rect" : [ 5.0, 218.0, 48.0, 20.0 ],
					"text" : "Score:"
				}
			},
			{
				"box" : 				{
					"comment" : "Routes score breakdown from js outlet 2",
					"id" : "obj-22",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 6,
					"outlettype" : [ "", "", "", "", "", "" ],
					"patching_rect" : [ 200.0, 540.0, 390.0, 22.0 ],
					"text" : "route family_score style_score tag_score attr_score prov_score"
				}
			},
			{
				"box" : 				{
					"id" : "obj-23",
					"maxclass" : "message",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 200.0, 575.0, 390.0, 22.0 ]
				}
			}
		],
		"lines" : [
			{
				"patchline" : 				{
					"source" : [ "obj-1", 0 ],
					"destination" : [ "obj-2", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-4", 0 ],
					"destination" : [ "obj-3", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-3", 0 ],
					"destination" : [ "obj-6", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-6", 0 ],
					"destination" : [ "obj-2", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-5", 0 ],
					"destination" : [ "obj-7", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-7", 0 ],
					"destination" : [ "obj-2", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-2", 0 ],
					"destination" : [ "obj-8", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-2", 1 ],
					"destination" : [ "obj-9", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-9", 0 ],
					"destination" : [ "obj-10", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-9", 1 ],
					"destination" : [ "obj-11", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-9", 2 ],
					"destination" : [ "obj-12", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-9", 3 ],
					"destination" : [ "obj-13", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-9", 4 ],
					"destination" : [ "obj-14", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-2", 2 ],
					"destination" : [ "obj-22", 0 ]
				}
			},
			{
				"patchline" : 				{
					"source" : [ "obj-22", 0 ],
					"destination" : [ "obj-23", 0 ]
				}
			}
		]
	}
}
